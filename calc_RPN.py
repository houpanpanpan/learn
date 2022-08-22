class Stack():
    """定义一个栈"""

    def __init__(self,):
        self.stack = []

    def push(self, data):#入栈
        self.stack.append(data)

    def pop(self):#出栈
        return self.stack.pop()

    def is_empty(self):#是否栈空
        return not len(self.stack)

    def top(self):#栈顶元素
        if self.is_empty():
            return None
        return self.stack[-1]


def find_errors(string):
    """检查输入是否存在错误,若存在错误返回假，否则返回真。"""
    str1 = "0123456789+-*/()."
    flag = True
    m = 0
    for i in string:
        if i not in str1:
            print("输入错误")
            flag = False
            break
        elif i not in ['*','/','+','-']:
            m = 0
        elif i in ['*','/','+','-']:
            m += 1
        if m == 2:
            print("输入格式错误")
            flag = False
            break
    return flag
    
def process(string):
    """对负数进行处理，如将-1变为0-1，并且将处理后的结果返回"""
    a = string
    b = 0
    for j in range(0, len(string)):
            if string[j]=='-' and string[j-1]=='(':
                a = a[0:j+b] + '0' + a[j+b:]
                b += 1       
    if string[0]=='-' or string[0]=='+':
        a = '0' + a
    return a
                
  
class InversPolishCalculator(object):
    """"逆波兰计算器"""

    def deal(self, string):
        """主程序,传入中缀表达式,返回结果"""
        list_expression = self.get_list_expression(string)
        stack = Stack()  # 实例化栈
        for ele in list_expression:  
            # 处理逆波兰表达式
            if ele.replace('.','').isdigit():
                # 是数字压入栈
                stack.push(ele)
            else:  
                # 是运算符进行运算,用次顶元素,和栈顶元素
                ret = self.operation(ele, float(stack.pop()), float(stack.pop()))
                stack.push(ret)
        return  stack.pop()#返回结果

    def operation(self, sign, num2, num1):
        """对数据进行运算，并返回运算结果"""
        if sign == '*':
            return num1 * num2
        if sign == '/':
            return num1 / num2
        if sign == '+':
            return num1 + num2
        if sign == '-':
            return num1 - num2

    def deal_str(self, string):
        """处理中缀表达式字符串,转为列表形式方便计算"""
        status = 0
        res = ''
        string = string.replace(' ','')
        for ele in string:
            if ele.isdigit() or ele =='.':
                if status == 1:
                    res = res.strip(' ')
                    res = res + ele + ' '
                else:
                    status = 1
                    res = res + ele + ' '
            else:
                status = 0
                res = res + ele + ' '
        return res.strip().split(' ')

    def get_list_expression(self, string):
        """将中缀表达式列表形式转后缀形式，并返回转换后的列表"""
        lst = self.deal_str(string)
        s1 = Stack()#操作符栈
        s2 = Stack()#数字栈
        for ele in lst:
            if ele.replace('.','').isdigit():
                s2.push(ele)
            else:
                self.deal_symbol(ele, s1, s2)
        while not s1.is_empty():
            s2.push(s1.pop())
        res = []
        while not s2.is_empty():
            res.append(s2.pop())
        return res[::-1]

    def deal_symbol(self, ele, s1, s2):
        """处理符号入栈出栈问题"""
        if s1.is_empty() or s1.top()=='(' or ele=='(':
            s1.push(ele)
        elif ele == ')':
            while s1.top() != '(':
                s2.push(s1.pop())
            s1.pop()
        elif self.get_priority(ele) > self.get_priority(s1.top()):
            s1.push(ele)
        else:
            s2.push(s1.pop())
            self.deal_symbol(ele, s1, s2)

    def get_priority(self, sign):
        """获取符号的优先级"""
        if sign=='*' or sign=='/':
            return 2
        elif sign=='+' or sign=='-':
            return 1


if __name__ == '__main__':
    """计算输入表达式"""
    str1 = input('请输入计算公式:')
    str2 = process(str1)
    if not find_errors(str2):
        print("请重新输入")
    else:
        Calculator = InversPolishCalculator()
        result = Calculator.deal(str2)
        print('计算结果:', result)
    
