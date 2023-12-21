import pyperclip
from colorama import Fore, Style, init
from typing import List, Tuple, Optional

init(autoreset=True)

RELEASE = True

MSG_CUT_LEN = 60

INPUT_ALIGN_CHAR_NUM: int = 40
TABLE_ALIGN_CHAR_NUM: int = 15
TABLE_ALIGN_CHAR_CMP: int = 3

COLOR_Input         = Fore.CYAN
COLOR_Input_Tip     = Fore.LIGHTWHITE_EX
COLOR_Input_Confirm = Fore.GREEN
COLOR_Title         = Fore.LIGHTWHITE_EX
COLOR_RowChr_New    = Fore.GREEN
COLOR_RowChr_Chars  = Fore.LIGHTBLACK_EX
COLOR_RowIdx_Normal = Fore.LIGHTBLACK_EX
COLOR_RowIdx_HiLite = Fore.GREEN


def get_data_from_clipboard() -> List[List[int]]:
    try:
        # 获取剪贴板内容并剔除首尾的"["和"]"
        data_str = pyperclip.paste().strip('[]')
        # 清理输入数据，去除任何非数字和逗号的字符
        data_str = ''.join(ch for ch in data_str if ch.isdigit() or ch == ',' or ch == '\n')
        # 将字符串转换为列表
        data = [list(map(int, row.split(','))) for row in data_str.split('\n') if row]
        return data
    except Exception as e:
        print(f"获取剪贴板内容时出错: {e}")
        return []


def add_to_data(data: List[List[int]], start_row: int, end_row: int, index: int, change: int) -> List[List[int]]:
    if not data:
        raise ValueError("Data must be not empty")
    if end_row - start_row < 1:
        raise ValueError("end row index must be greater than start row index")

    for i in range(start_row - 1, end_row):
        if len(data[i]) > index:
            if change == -1:
                data[i].pop(index)
            else:
                data[i][index] += change
        elif len(data[i]) == index:
            if change == -1:
                raise ValueError("cannot add a delete operation.")
            else:
                data[i].append(change)
        else:
            raise ValueError(f"data index out of range-- try: {index} data: {len(data[i])}")
    return data


def get_message(data: List[List[int]], modified_rows=None, modified_index: int = -1) -> str:
    if modified_rows is None:
        modified_rows = []
    msg = []
    for i in range(len(data)):
        # index number
        idx_color = COLOR_RowIdx_HiLite if i % 10 == 0 else COLOR_RowIdx_Normal
        row_str = f"{idx_color}{(i + 1):3}: {Style.RESET_ALL}"
        # content
        for j in range(len(data[i])):
            num_str = f'{data[i][j]:{6}}'
            if i in modified_rows and j == modified_index:
                num_str = COLOR_RowChr_New + num_str + Fore.RESET
            row_str += f'{num_str}{COLOR_RowChr_Chars},{Fore.RESET}'
        # message
        msg.append(row_str)

    columned_msg = []
    # calc align len
    align_len: int = max(len(item.split(',')) for item in msg) * TABLE_ALIGN_CHAR_NUM
    # append
    for icm in range(MSG_CUT_LEN):
        row = ""
        for im in range(len(msg)):
            unit_cnt: int = len(msg[im].split(','))
            if im % MSG_CUT_LEN == icm:
                row += f"{msg[im] + (' ' * TABLE_ALIGN_CHAR_CMP * int(unit_cnt / 2)):<{align_len}}"
        columned_msg.append(f"{row}\n")

    return "".join(columned_msg)


def copy_to_clipboard(data: List[List[int]]) -> None:
    try:
        data_str = ""
        for row in data:
            row_str = ", ".join(map(str, row))
            data_str += f"[{row_str}]\n"
        pyperclip.copy(data_str)
    except Exception as e:
        print(f"复制到剪贴板时出错: {e}")


last_scope: Tuple[int, int] = (-1, -1)


def get_last_scope(index: int) -> Tuple[int, int]:
    if last_scope[index] == -1:
        raise ValueError(f"last scope is {last_scope}, cannot get index {index}.")
    return last_scope[index]


def program() -> None:
    # data
    data: List[List[int]] = get_data_from_clipboard()
    if data is None or len(data) == 0:
        raise ValueError("clipboard is None.")
    print(f"{COLOR_Title}\n剪贴板内容:\n" + get_message(data))

    # scope
    scope: Optional[Tuple[int, int]] = None
    while scope is None:
        try:
            tip = f"{COLOR_Input}{f'input scope{COLOR_Input_Tip}(start end)(-){COLOR_Input}':<{INPUT_ALIGN_CHAR_NUM}}: "
            scope_input: List[str] = list(input(tip).split())
            if len(scope_input) != 2:
                raise ValueError("more than one scope input")
            scope = (
                1                 if scope_input[0] == "-" else
                get_last_scope(0) if scope_input[0] == " " else
                int(scope_input[0]),
                len(data)         if scope_input[1] == "-" else
                get_last_scope(1) if scope_input[1] == " " else
                int(scope_input[1]))
        except ValueError as ex:
            print(f"\n{Fore.RED}Err: 输入的值不正确: {ex}")

    # index
    indexes: Optional[List[int]] = None
    while indexes is None:
        try:
            tip = f"{COLOR_Input}{f'input index{COLOR_Input_Tip}(start on 1){COLOR_Input}':<{INPUT_ALIGN_CHAR_NUM}}: "
            indexes = list(map(lambda s: int(s) - 1, input(tip).split()))
        except ValueError as ex:
            print(f"\n{Fore.RED}Err: 输入的值不正确: {ex}")

    # changes
    changes: Optional[List[int]] = None
    while changes is None:
        try:
            tip_list = [i + 1 for i in indexes]
            tip = f"{COLOR_Input}{f'input changes on {COLOR_Input_Tip}{tip_list}{COLOR_Input}':<{INPUT_ALIGN_CHAR_NUM}}: "
            changes = list(map(int, input(tip).split()))
        except ValueError as ex:
            print(f"\n{Fore.RED}Err: 输入的值不正确: {ex}")

    # check
    if len(indexes) != len(changes):
        raise ValueError(f"\n{Fore.RED}Err: 下标和修改必须一一对应: \n{indexes} \n{changes}")

    # process
    for i in range(len(changes)):
        data = add_to_data(
            data=data,
            start_row=scope[0], end_row=scope[1],
            index=indexes[i],
            change=changes[i])
        print("\n当前值:\n" + get_message(data, list(range(scope[0] - 1, scope[1])), indexes[i]))

    if input(f"{COLOR_Input_Confirm}apply{COLOR_Input_Tip}(y/n){COLOR_Input_Confirm}? ") == 'y':
        copy_to_clipboard(data)
        print("已复制到剪贴板")

        global last_scope
        last_scope = (scope[0], scope[1])


if __name__ == "__main__":
    while True:
        try:
            command = input(f"{COLOR_Input}\ninput command: ")
            if command.lower() == "exit":
                pass
            elif command.lower() == "get":
                program()
        except Exception as err:
            print(f"\n{Fore.RED}Fatal: 运行时错误: {err}")
            if not RELEASE:
                raise err
