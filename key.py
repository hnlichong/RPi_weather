def write():
    # write into file
    f_name = now.strftime('%Y%m%d') + '.csv'
    f_path = os.path.join(env_path, f_name)
    if not os.path.exists(f_path):
        with open(f_path, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(env_fields)
            writer.writerow(data)
    else:
        with open(f_path, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(data)
