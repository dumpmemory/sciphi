# SciPhi [<span style="color:gold">ΨΦ</span>]: A Framework for LLM Powered Data

<p align="center">
<img width="716" alt="SciPhi Logo" src="https://github.com/emrgnt-cmplxty/sciphi/assets/68796651/195367d8-54fd-4281-ace0-87ea8523f982">
</p>

SciPhi is a Python-based framework designed to facilitate the generation of high-quality synthetic data tailored for both Large Language Models (LLMs) and human users. This suite offers:

- **Configurable Data Generation:** Craft datasets mediated by LLMs according to your specifications.
- **Retriever-Augmented Generation (RAG) Integration:** Make use of an integrated RAG Provider API to ground your generated data to real-world datasets. Also, SciPhi comes bundled with an evaluation harness to optimise your RAG workflow.
- **Textbook Generation Module:** A module to power the generation of RAG-augmented synthetic textbooks straight from a given table of contents.

---

## Fast Setup

```bash
pip install sciphi
```

### Optional Dependencies

Install with specific optional support using extras:

- **Anthropic**: `'sciphi[anthropic_support]'`
- **HF (includes Torch)**: `'sciphi[hf_support]'`
- **Llama-CPP**: `'sciphi[llama_cpp_support]'`
- **Llama-Index**: `'sciphi[llama_index_support]'`
- **VLLM (includes Torch)**: `'sciphi[vllm_support]'`
- **All (no vLLM)**: `'sciphi[all]'`
- **All (with extras, e.g. vLLM)**: `'sciphi[all_with_extras]'`

### **Recommended** (All Optional Dependencies):

```bash
pip install 'sciphi[all_with_extras]'
```

### **Setup Your Environment**:

   Navigate to a working directory and use a text editor to adjust the `.env` file with your specific configurations.

  ```bash
  # Proprietary Providers
  OPENAI_API_KEY=your_openai_key
  ANTHROPIC_API_KEY=your_anthropic_key
  # Open Source Providers
  HF_TOKEN=your_huggingface_token
  # vLLM
  VLLM_API_KEY=your_vllm_token
  # RAG Provider Settings
  RAG_API_BASE=your_rag_server_base_url
  RAG_API_KEY=your_rag_server_key
  ```
  After entering your settings, ensure you save and exit the file.

---

## Features

### Community & Support

- Engage with our vibrant community on [Discord](https://discord.gg/j9GxfbxqAe).
- For tailored inquiries or feedback, please [email us](mailto:owen@sciphi.ai).

### Configurable Data Generation

Running the data_augmenter with an input dataset and prompt configuration will generate a new dataset with the specified number of samples.
```bash
python -m sciphi.scripts.data_augmenter.py --config-path=$PWD/sciphi/config/prompts/question_and_answer.yaml --config_name=None --n_samples=1
```

  We can readily examine the the output of this command: 

  ```bash
  tail augmented_output/config_name__question_and_answer_dataset_name__ContextualAI_tiny-wiki100-chunks.jsonl
  {"question": "What is the reaction called when alcohol and carboxylic acids react?", "answer": "Fischer esterification"}
  {"question": "What is the catalyst usually required for Fischer esterification?", "answer": "concentrated sulfuric acid"}
  {"question": "How are tosyl esters made?", "answer": "by reaction of the alcohol with p-toluenesulfonyl chloride in pyridine"}
  {"question": "What are primary alcohols oxidized to?", "answer": "aldehydes or carboxylic acids"}
  {"question": "What is the final product of the oxidation of secondary alcohols?", "answer": "ketone"}
  {"question": "Are tertiary alcohols resistant to oxidation?", "answer": "Yes"}
  ```

### Textbook Generation

This is an effort to democratize access to top-tier textbooks. This can readily be extended to other domains, such as internal commercial documents.

#### Generating Textbooks

1. **Dry Run**:
   ```bash
   python -m sciphi.scripts.textbook_generator dry_run --toc_dir=sciphi/data/sample/table_of_contents --rag-enabled=False
   ```

    This will perform a dry-run over the default textbooks stored in `sciphi/data/sample/textbooks`.

    _Note_ - this must be run from the root of the repository, or else you will need to update the `toc_dir` accordingly. Setting rag-enabled to `True` will enable RAG augmentation during the generation process. You may customize the RAG provider through additional arguments.

2. **Textbook Generation**:
   ```bash
   python -m sciphi.scripts.textbook_generator run --toc_dir=sciphi/data/sample/table_of_contents --rag-enabled=False
   ```

   Replace `dry_run` above with `run` to generate one textbook for each table of contents in the target directory. See a [sample textbook here.](sciphi/data/sample/textbooks/Aerodynamics_of_Viscous_Fluids.md)

3. **Example With a Custom Table of Contents**:

   Prepare your table of contents and save it into `$PWD/toc/test.yaml`. Then, run the following command:
   ```bash
   python -m sciphi.scripts.generate_textbook run --toc_dir=toc --output_dir=books --data_dir=$PWD
   ``````
   For help with formatting your table of contents, [see here](https://github.com/SciPhi-AI/sciphi/blob/main/sciphi/data/library_of_phi/table_of_contents/Aerodynamics_of_Viscous_Fluids.yaml).

4. **Custom Settings & RAG Functionality**:

   Simply switch `rag-enabled` to `True`. Ensure you have the right `.env` variables set up, or provide CLI values for `rag_api_base` and `rag_api_key`.
   
   Alternatively, you may provide your own custom settings in a YAML file. See the [default settings configuration here](sciphi/config/generation_settings/textbook_generation_settings.yaml).

_Important:_ To make the most out of grounding your data with Wikipedia, ensure your system matches our detailed specifications. An example RAG provider can be seen [here](https://github.com/SciPhi-AI/sciphi/blob/main/sciphi/interface/rag/sciphi_wiki.py). More high quality outbook books are available [here](https://github.com/SciPhi-AI/library-of-phi).

### RAG Eval Harness

To measure the efficacy of your RAG pipeline, we provide a unique RAG evaluation harness.

#### Running the RAG Harness
   ```bash
   python -m sciphi.scripts.rag_harness --n-samples=100 --rag-enabled=True --evals_to_run="science_multiple_choice"
   ```
  This example runs over 100 science multiple choice questions with RAG enabled and reports the final accuracy.

---

## Local Development

### Local setup
1. **Clone the Repository**:
   
   Begin by cloning the repository and stepping into the project directory:
   ```bash
   git clone https://github.com/emrgnt-cmplxty/sciphi.git
   cd sciphi
   ```

2. **Install the Dependencies**:

   Start by installing the primary requirements:
   ```bash
   pip install -r requirements.txt
   ```

   If you require further functionalities, consider the following:
   - For the developer's toolkit and utilities:
     ```bash
     pip install -r requirements_dev.txt
     ```

   - To encompass all optional dependencies:
     ```bash
     pip install -r requirements_all.txt
     ```

   Alternatively, to manage packages using Poetry:
   ```bash
   poetry install
   ```

     And for optional dependencies w/ Poetry:
     ```bash
     poetry install -E [all, all_with_extras]
     ```
     
3. **Example - Create your own LLM and RAG provider**:

   ```python
   from sciphi.core import LLMProviderName, RAGProviderName
   from sciphi.interface import LLMInterfaceManager, RAGInterfaceManager

       llm_interface = LLMInterfaceManager.get_interface_from_args(
           provider_name=LLMProviderName(llm_provider_name),
           model_name=llm_model_name,
           # Additional args
           max_tokens_to_sample=llm_max_tokens_to_sample,
           temperature=llm_temperature,
           top_k=llm_top_k,
           # Used for re-routing requests to a remote vLLM server
           server_base=kwargs.get("llm_server_base", None),
       )
   
       rag_interface = (
           RAGInterfaceManager.get_interface_from_args(
               provider_name=RAGProviderName(rag_provider_name),
               base=rag_api_base or os.environ.get("RAG_API_BASE"),
               token=rag_api_key or os.environ.get("RAG_API_KEY"),
               max_context=rag_max_context,
               top_k=rag_top_k,
           )
           if rag_enabled
           else None
       )
      # ... Continue ...
   ```
   Supported LLM providers include OpenAI, Anthropic, HuggingFace, and vLLM. For RAG database access, configure your own, or get access to the SciPhi **gigaRAG API**.
---

## System Requirements

### Essential Packages:

- **Python Version**: `>=3.9,<3.12`

- **Required Libraries**:
  - `bs4`: `^0.0.1`
  - `fire`: `^0.5.0`
  - `openai`: `0.27.8`
  - `pandas`: `^2.1.0`
  - `python-dotenv`: `^1.0.0`
  - `pyyaml`: `^6.0.1`
  - `retrying`: `^1.3.4`
  - `sentencepiece`: `^0.1.99`
  - `torch`: `^2.1.0`
  - `tiktoken`: `^0.5.1`
  - `tqdm`: `^4.66.1`

### Supplementary Packages:

- **Anthropic Integration**:
  - `anthropic`: `^0.3.10`
- **Hugging Face Tools**:
  - `accelerate`: `^0.23.0`
  - `datasets`: `^2.14.5`
  - `transformers`: `^4.33.1`
- **Llama-Index**:
  - `llama-index`: `^0.8.29.post1`
- **Llama-CPP**:
  - `llama-cpp-python`: `^0.2.11`
- **VLLM Tools**:
  - `vllm`: `0.2.0`

---

## Licensing and Acknowledgment

This project is licensed under the [Apache-2.0 License](./LICENSE).

### Citing Our Work

If SciPhi plays a role in your research, we kindly ask you to acknowledge us with the following citation:

```plaintext
@software{SciPhi,
author = {Colegrove, Owen},
doi = {Pending},
month = {09},
title = {{SciPhi: A Framework for LLM Powered Data}},
url = {https://github.com/sciphi-ai/sciphi},
year = {2023}
}
```
