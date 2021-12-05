import os

start_index = 10000
offset = 100
end_index = 50000

index = start_index

while index + offset < end_index:
    if not os.path.isfile("../crawled_data_Tranco/crawl_" + str(index) + "-" + str(index + offset) + ".sqlite"):
        print("crawl_" + str(index) + "-" + str(index + offset))
    if not os.path.isfile("../crawled_data_Tranco/crawl_" + str(index) + "-" + str(index + offset) + "_privacy.sqlite"):
        print("crawl_" + str(index) + "-" + str(index + offset) + "_privacy")
    
    index += offset
