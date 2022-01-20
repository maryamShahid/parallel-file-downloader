# ParallelFileDownloader

A program that downloads an index file to obtain a list of text file URLs and download these files in parallel using multithreading.

### How to Run:

```
python3 ParallelFileDownloader.py <index_file> <connection_count>
```
where <index_file> is the URL of the index that includes a list of text file URLs to be downloaded and <connection_count> is the number of thread connections to be established for each file URL.

