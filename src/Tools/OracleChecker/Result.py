from typing import List, Tuple, Optional, Union,Sequence
from time import time
import pymysql
from sqlalchemy import create_engine, text
class Result:
    def __init__(self, column_names: List[str], column_types: List[str], rows: List[List[str]], err: Optional[Exception] = None):
        self.column_names = column_names
        self.column_types = column_types
        self.rows = rows
        self.err = err  
    def to_string(self) -> str:
        result_str = "ColumnName(ColumnType)s: "
        result_str += " ".join([f"{name}({type_})" for name, type_ in zip(self.column_names, self.column_types)])
        result_str += "\n"
        for i, row in enumerate(self.rows):
            result_str += f"row {i}: {' '.join(row)}\n"
        if self.err:
            result_str += f"Error: {self.err}\n"
        return result_str

    def flat_rows(self) -> List[str]:
        return [",".join(row) for row in self.rows]

    def is_empty(self) -> bool:
        return len(self.column_names) == 0

    def get_error_code(self) -> Tuple[int, Optional[Exception]]:
        if not self.err:
            return -1, Exception("[Result.GetErrorCode]result.err == None")
        else:
            return -1, Exception(f"[Result.GetErrorCode]not mysql.connector.Error {type(self.err).__name__}")

    def cmp(self, another: 'Result') -> Tuple[int, Optional[Exception]]:
        if self.err:
            return -2, Exception("[Result.CMP]self error")
        if another.err:
            return -2, Exception("[Result.CMP]another error")
        # 判断两个结果集是否为空
        empty1 = self.is_empty()
        empty2 = another.is_empty()

        # 若两个结果集其中一个为空
        if empty1 or empty2:
            # 都为空则说明两个结果集相等
            if empty1 and empty2:
                return 0, None
            return (-1, None) if empty1 else (1, None)
        
        if len(self.column_names) != len(another.column_names):
            return 2, None
        
        res1 = self.flat_rows()
        res2 = another.flat_rows()
        
        mp = {}
        # 遍历res2，如果元素r已在字典中，就将其频次加1；否则将其初始频次设置为1。
        for r in res2:
            mp[r] = mp.get(r, 0) + 1
        
        all_in_another = True
        # 检查res1中的元素是否存在于res2中
        for r in res1:
            if r in mp:
                # 若它的频次只有1，则从字典中删除该元素；若频次大于1，则将频次减1。
                if mp[r] <= 1:
                    del mp[r]
                else:
                    mp[r] -= 1
            else:
                # 将all_in_another置为False，表示res1存在元素不在res2中。
                all_in_another = False

        # 如果res1所有的元素都在res2中（all_in_another == True）：
        # mp为空（res2中的所有元素都已匹配完成）：返回(0, None)，表示两个列表完全相等。
        # 若非mp空：返回(-1, None)，表示res1是res2的子集，但res2还有多余元素。

        # 如果res1某些元素不在res2中（all_in_another == False）：
        # mp为空：返回(1, None)，表示res1有多余元素，但res2正好用尽。表示res2是res1的子集，但res1还有多余元素。
        # 若非mp空：返回(2, None)，表示res1和res2都有不匹配的地方。
        if all_in_another:
            if not mp:
                return 0, None
            return -1, None
        else:
            if not mp:
                return 1, None
            return 2, None
        
if __name__=="__main__":
    column_names = ["ID", "Name", "Age"]
    column_types = ["int", "string", "int"]
    rows = [
        ["1", "Alice", "30"],
        ["2", "Bob", "25"],
        ["3", "Charlie", "35"]
    ]

    # 创建 Result 对象
    result = Result(column_names, column_types, rows)

    # 使用 to_string 方法打印 Result 的内容
    print("Result to_string output:")
    print(result.to_string())

    # 检查是否为空
    print("Is Result empty?")
    print(result.is_empty())  # 输出: False

    # 获取平坦化后的行数据
    print("Flat rows:")
    print(result.flat_rows())  # 输出: ['1,Alice,30', '2,Bob,25', '3,Charlie,35']

    # 创建另一个 Result 对象用于比较
    another_result = Result(column_names, column_types, [["2", "Bob", "25"], ["3", "Charlie", "35"]])

    # 比较两个 Result 对象
    print("Comparison result:")
    cmp_result, cmp_error = result.cmp(another_result)
    print(f"Comparison code: {cmp_result}, Error: {cmp_error}") # cmp_results=1：result是another_result的超集，another_result是result的子集