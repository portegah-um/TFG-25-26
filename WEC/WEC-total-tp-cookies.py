import json

def main():
    third_party_total_counter = 0
    first_party_total_counter = 0
    pages_analysed_counter = 0
    for i in range(1,101):
        try:
            with open("Results\\" + str(i) + ".json", 'r', encoding="utf8") as raw:
                data = json.load(raw)
            for cookie in data["cookies"]:
                if cookie.get("firstPartyStorage") == False:
                    third_party_total_counter += 1
                    break
            pages_analysed_counter += 1
        except:
            print("File not found, resuming...")
    print(third_party_total_counter)
    print(pages_analysed_counter)
    with open("Analysis-Results-Raw/third_party_total_used.txt", mode="w") as output:
        output.write(str(third_party_total_counter) + "," + str(pages_analysed_counter))
        output.close

if __name__=="__main__":
    main()