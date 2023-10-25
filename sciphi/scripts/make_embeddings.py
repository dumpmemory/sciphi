import gzip
import json
import logging
from typing import Dict, Generator, List, Tuple, Union

import fire
import numpy as np
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer

from sciphi.llm.embedding_helpers import process_documents

logger = logging.getLogger(__name__)


def stream_jsonl(
    file_path: str,
) -> Generator[Dict[str, Union[str, int]], None, None]:
    """
    Generator function to read a gzipped JSONL (JSON Lines) file line by line.

    Args:
    - file_path (str): Path to the gzipped JSONL file.

    Yields:
    - entry (Dict[str, Union[str, int]]): The dictionary entry from the JSONL file.
    """
    with gzip.open(file_path, "rt") as f:
        for line in f:
            entry = json.loads(line.strip())
            if "page_id" not in entry:
                continue
            yield entry


def reconstitute_sentences_into_chunks(
    df: pd.DataFrame,
    ids_to_titles: dict,
    chunk_size: int = 512,
    prepend_title_to_each_chunk: bool = True,
    truncate_long_chunks: bool = False,
) -> List[Tuple[int, str, str]]:
    """
    Splits sentences from the dataframe into chunks based on the given chunk size.

    Args:
    - df (pd.DataFrame): Dataframe containing document IDs and text.
    - ids_to_titles (Dict[int, str]): Mapping from document ID to title.
    - chunk_size (int, optional): Maximum size of a chunk. Default is 512.
    - prepend_title_to_each_chunk (bool, optional): Whether to prepend title to each chunk. Default is True.
    - truncate_long_chunks (bool, optional): Whether to truncate long chunks. Default is False.

    Returns:
    - List[Tuple[int, str, str]]: List of tuples containing document ID, title, and the chunk of text.
    """
    chunks: list = []
    current_chunk = ""
    current_length = 0
    title = None
    document_id = None

    for _, row in df.iterrows():
        document_id = row["document_id"]
        sentence = row["text"]
        title = ids_to_titles[document_id]
        if current_length + len(sentence) > chunk_size:
            chunks.append(
                (
                    document_id,
                    title,
                    current_chunk[:chunk_size]
                    if truncate_long_chunks
                    else current_chunk,
                )
            )
            current_chunk = (
                f"{title}:\n{sentence}"
                if prepend_title_to_each_chunk
                else sentence
            )
            current_length = len(current_chunk)
        else:
            if current_chunk:
                current_chunk += " "
            current_chunk += sentence
            current_length += len(sentence)

    if current_chunk:
        chunks.append((document_id, title, f"{title}:\n{current_chunk}"))
    return chunks


def save_embeddings_to_memmap(embeddings: np.ndarray, file_name: str) -> None:
    """
    Save embeddings in a memory-mapped format and also save the shape of the embeddings.

    Args:
    - embeddings (np.ndarray): Numpy array containing embeddings.
    - file_name (str): Path to the output file.
    """
    shape = embeddings.shape

    # Save the shape information to a separate file
    with open(f"{file_name}.shape", "w") as shape_file:
        shape_file.write(",".join(map(str, shape)))

    # Create a new memory-mapped array with the required shape and dtype
    memmap_array = np.memmap(
        file_name, dtype=embeddings.dtype, mode="w+", shape=shape
    )

    # Copy the embeddings data into the memory-mapped array
    memmap_array[:] = embeddings[:]

    # Flush memory changes to disk and close the memmap array
    memmap_array.flush()
    del memmap_array


def save_metadata_to_file(metadata: list, file_name: str) -> None:
    """
    Save metadata in a gzipped JSONL format.

    Args:
    - metadata (List[Dict[str, Union[int, str]]]): List of metadata entries.
    - file_name (str): Path to the output file.
    """
    with gzip.open(file_name, "at") as f_out:
        for entry in metadata:
            f_out.write(json.dumps(entry) + "\n")


def _load_shape_from_file(file_name: str) -> tuple:
    """Load shape of the memmap array from a file."""
    with open(f"{file_name}.shape", "r") as shape_file:
        shape_str = shape_file.read()
        shape = tuple(map(int, shape_str.split(",")))
    return shape


def fetch_embedding_and_metadata(
    embeddings_file: str, metadata_file: str, idx: int
) -> Tuple[np.ndarray, Dict[str, Union[int, str]]]:
    """
    Fetch the embedding and metadata for a given index.

    Args:
    - embeddings_file (str): Path to the memmap embeddings file.
    - metadata_file (str): Path to the gzipped metadata JSONL file.
    - idx (int): Index to fetch data for.

    Returns:
    - tuple: Embedding as a numpy array and metadata as a dictionary.
    """
    # Load the shape of the embeddings and create the memmap object
    shape = _load_shape_from_file(embeddings_file)
    memmap_array = np.memmap(
        embeddings_file, dtype="float32", mode="r", shape=shape
    )

    # Fetch the embedding for the given index
    embedding = memmap_array[idx]

    # Fetch the metadata for the given index
    with gzip.open(metadata_file, "rt") as f:
        for i, line in enumerate(f):
            if i == idx:
                metadata = json.loads(line.strip())
                break

    return embedding, metadata


def main(
    file_path: str = "sample.json.gz",
    model_name: str = "BAAI/bge-base-en",
    chunk_size: int = 512,
    batch_size: int = 128,
    embeddings_output_path: str = "embeddings.bin",
    metadata_output_path: str = "metadata.json.gz",
):
    """
    Main function to process a gzipped JSONL file and generate embeddings for text chunks.

    Args:
    - input_file_path (str, optional): Path to the gzipped JSONL file. Default is 'sample.json.gz'.
    - model_name (str, optional): Model name for sentence transformer. Default is 'BAAI/bge-base-en'.
    - chunk_size (int, optional): Maximum size of a chunk. Default is 512.
    - batch_size (int, optional): Maximum size of a batch. Default is 128.
    - embeddings_output_path (str, optional): Path to save embeddings. Default is 'embeddings.gz'.
    - metadata_output_path (str, optional): Path to save metadata. Default is 'metadata.json.gz'.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer(model_name).to(device)
    document_ids: list = []
    documents: list = []
    ids_to_titles: dict = {}

    for entry in stream_jsonl(file_path):
        document_ids.append(entry["page_id"])
        documents.append(entry["text"])
        ids_to_titles[entry["page_id"]] = entry["title"]
        if len(document_ids) == batch_size:
            df = process_documents(documents, document_ids)
            chunks = reconstitute_sentences_into_chunks(
                df, ids_to_titles, chunk_size
            )
            chunk_embedding = model.encode(
                [entry[-1] for entry in chunks],
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            # Save embeddings and metadata
            save_embeddings_to_memmap(chunk_embedding, embeddings_output_path)
            metadata_list = [
                {"doc_id": entry[0], "title": entry[1], "text_chunk": entry[2]}
                for entry in chunks
            ]
            save_metadata_to_file(metadata_list, metadata_output_path)

            # Reset lists for the next batch
            document_ids = []
            documents = []
            ids_to_titles = {}


if __name__ == "__main__":
    fire.Fire(main)