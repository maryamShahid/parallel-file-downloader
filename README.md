# ParallelFileDownloader

CLI application downloads an index file to obtain a list of text file URLs and download these files in parallel by multi-threading.

If the requested file is found in the server, the response is a 200 OK message. When this is the case, the program establishes <connection_count> parallel connections with the server including the file, downloads non-overlapping parts of the file through these connections, constructs and saves the file under the directory in which the program runs.

## How to Run:

```
python3 ParallelFileDownloader.py <index_file> <connection_count>
```
where <index_file> is the URL of the index that includes a list of text file URLs to be downloaded and <connection_count> is the number of thread connections to be established for each file URL.

## Test URLs:

* www.cs.bilkent.edu.tr/~cs421/fall21/project1/index1.txt
* www.cs.bilkent.edu.tr/~cs421/fall21/project1/index2.txt

