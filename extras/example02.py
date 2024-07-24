FILENAME_IN = "MOCK_DATA.csv"
FILENAME_OUT = "MOCK_DATA_RST.csv"


def full_read(in_file: str):
    with open(in_file) as my_file:
        return my_file.read()


def read_file(in_file: str):
    with open(in_file, 'r') as fi:
        line = fi.readline()
        while line:
            line = fi.readline()
            yield line


def write_file(out_file: str, content: str):
    with open(out_file, "a") as my_file:
        my_file.write(content)


def processar_content(content: str):
    pass


if __name__ == '__main__':
    # content = full_read(FILENAME_IN)
    # processar_content(content)
    # write_file(FILENAME_OUT, content)


    for line in read_file(FILENAME_IN):
        write_file(FILENAME_OUT, line)
        user_input = input("Para processar a próxima linha digite <ENTER>. Para encerrar digite algum caracter.")
        if bool(user_input):
            break
