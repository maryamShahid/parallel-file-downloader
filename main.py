import socket
import os
import threading
import math
import sys
from urllib import parse

indexURL = ''
threadCount = 3

if sys.argv[1]:
    indexURL = str(sys.argv[1])
    # print(indexURL)

if len(sys.argv) == 3:
    threadCount = int(str(sys.argv[2]))


def parseURL(url):
    url = 'https://' + url
    splitUrl = parse.urlsplit(url)
    return splitUrl


def getRequest(path, ipAddr):
    getReq = "GET " + path + " HTTP/1.0\r\nHost: " + ipAddr + "\r\n\r\n"
    getReq = str.encode(getReq)
    sock.send(getReq)


def headRequest(path, ipAddr):
    headReq = "HEAD " + path + " HTTP/1.0\r\nHost: " + ipAddr + "\r\n\r\n"
    headReq = str.encode(headReq)
    sock.send(headReq)


def getRangeRequest(lowerBound, upperBound, path, ipAddr):
    lowerBound = str(lowerBound)
    upperBound = str(upperBound)
    getReq = "GET " + path + " HTTP/1.1\r\nHost: " + ipAddr + "\r\n" "Range: bytes=  " + lowerBound + '-' + upperBound + "\r\n\r\n"
    getReq = str.encode(getReq)
    sock.send(getReq)


def getContentLength(fileContent):
    length = 0
    start = fileContent.find('Content-Length')
    end = fileContent.find('Connection', start)
    contentLength = fileContent[start:end]
    if contentLength:
        length = [int(length) for length in contentLength.split() if length.isdigit()]
        length = length[0]
    return length


def findNumberOfFiles(indexFileData):
    flag = True
    start = 0
    count = 0
    while flag:
        a = indexFileData.find('www', start)
        if a == -1:
            flag = False
        else:
            count += 1
            start = a + 1
    return count


def thread_function(startByte, endByte, nextIPAddress, nextPath):
    getRangeRequest(startByte, endByte, nextPath, nextIPAddress)

    fileData = ''
    while True:
        data = sock.recv(4096)
        if not data:
            break
        fileData += data.decode("utf-8")

    print('filedate ', fileData)

    lineTextData = fileData.rsplit('plain', 1)[-1]
    formattedLineTextData = os.linesep.join([s for s in lineTextData.splitlines() if s])

    if formattedLineTextData:
        fileName = nextPath.rsplit('/', 1)[-1]
        textFile = open(fileName, "w+")
        textFile.seek(startByte)
        textFile.write(formattedLineTextData)

    print(str(startByte) + ':' + str(endByte) + '(' + str(endByte + 1) + ')')


if indexURL:
    # parse index url
    splitUrl = parseURL(indexURL)
    urlPath = splitUrl.path

    # connect to socket
    ipAddress = socket.gethostbyname(splitUrl.netloc)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ipAddress, 80))

    # get request on index file
    getRequest(urlPath, ipAddress)

    # get contents of index file
    fileData = ''
    while True:
        data = sock.recv(4096)
        if not data:
            break
        fileData += data.decode("utf-8")

    print('URL of the index file: ' + indexURL)
    print('Index file is downloaded')
    print('There are ' + str(findNumberOfFiles(fileData)) + ' files in the index')

    # initialise array of urls from index file
    stringOfFiles = fileData
    startSecond = stringOfFiles.find('www')
    stringOfFiles = stringOfFiles[startSecond:]
    arrayOfFiles = stringOfFiles.splitlines()

    for i in range(len(arrayOfFiles)):
        # parse URL of file
        nextUrl = arrayOfFiles[i]
        splitNextUrl = parseURL(nextUrl)
        nextPath = splitNextUrl.path
        nextIPAddress = socket.gethostbyname(splitNextUrl.netloc)

        # send HEAD request to check response
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((nextIPAddress, 80))
        headRequest(nextPath, nextIPAddress)

        # receive response of HEAD request
        fileData = ''
        while True:
            data = sock.recv(4096)
            if not data:
                break
            fileData += data.decode("utf-8")
            # print(fileData)

        # if head request is 200 OK
        if '200 OK' in fileData:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((nextIPAddress, 80))

            n = getContentLength(fileData)
            print(str(i + 1) + '. ' + nextUrl + ' (size = ' + str(n) + ') is downloaded')
            print('File parts:')

            if n % threadCount == 0:
                byteCount = int(n / threadCount)

                for threadNumber in range(threadCount):
                    start = byteCount * threadNumber
                    end = start + byteCount - 1

                    t = threading.Thread(target=thread_function, args=(start, end, nextIPAddress, nextPath))
                    t.start()

            else:
                modThreads = n % threadCount
                remainingThreads = threadCount - modThreads
                floorBytes = math.floor(n / threadCount)
                floorBytesAddOne = floorBytes + 1
                modEndByte = 0

                # modThreads will download floorBytesAddOne
                for threadNumber in range(modThreads):
                    start = floorBytesAddOne * threadNumber
                    end = start + floorBytesAddOne - 1
                    modEndByte = end

                    t = threading.Thread(target=thread_function, args=(start, end, nextIPAddress, nextPath))
                    t.start()

                secondStart = modEndByte + 1
                secondEnd = secondStart + floorBytes - 1
                # remainingThreads will download floorBytes
                for threadNumber in range(remainingThreads):
                    t = threading.Thread(target=thread_function, args=(secondStart, secondEnd, nextIPAddress, nextPath))
                    t.start()

                    secondStart = secondEnd + 1
                    secondEnd = secondStart + floorBytes - 1

        # if head request is 404 not found
        else:
            print(str(i + 1) + '. ' + nextUrl + ' is not found')

        main_thread = threading.current_thread()
        for t in threading.enumerate():
            if t is main_thread:
                continue
            t.join()

