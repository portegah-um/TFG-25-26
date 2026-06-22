import json

def main():
    has_cookie_counter = 0
    pages_analysed_counter = 0
    for i in range(1,1001):
        try:
            with open("Results\\" + str(i) + ".json", 'r', encoding="utf8") as raw:
                data = json.load(raw)
            if data["cookies"]:
                has_cookie_counter += 1
            pages_analysed_counter += 1
        except:
            print("File not found, resuming...")
    print(has_cookie_counter)
    with open("cookie_nocookie.csv", mode="w") as output:
        output.write(str(has_cookie_counter) + "," + str(pages_analysed_counter))
        output.close()

if __name__=="__main__":
    main()