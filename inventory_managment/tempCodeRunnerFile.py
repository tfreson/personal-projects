for item_name, cur_item in cur_dict.items():
        prev_item = prev_dict.get(item_name)
        if prev_item:
            diff[item_name] = cur_item[3] - prev_item[3]
        else:
            diff[item_name] = cur_item[3]
    print(f"Diff in counts for {date}: {diff}")
