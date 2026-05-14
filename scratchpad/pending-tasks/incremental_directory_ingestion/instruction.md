Repeatedly uploading an entire directory to a managed LlamaCloud index wastes compute resources, slows down the pipeline, and can lead to duplicate document chunks.

You need to create an incremental sync script `sync_folder.py` that scans a local `./docs` directory and compares file modification timestamps against a local state file named `sync_state.json`. The script must identify new or modified files, upload ONLY those files to an existing `LlamaCloudIndex` named "live_docs", and then update `sync_state.json` with the new timestamps. 

**Constraints:**
- Must not re-upload files that haven't been modified since the last sync.
- Must handle the case where `sync_state.json` does not exist (initial run).
- Must use LlamaCloud Index APIs to insert the new documents into the existing managed index.