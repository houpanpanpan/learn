import re

oper_char = ['*','/','-','+']

def format_str(s):
    '''除去空格和两边括号'''
    return s.replace(' ','').replace('(','').replace(')','')

def error(s):
    '''检查输入是否存在错误'''
    
    str1 = "0123456789-+*/(). "
    flag = True
    for i in s:
        if i not in str1:
            print("输入错误")
            flag = False
            break
                
        if i in oper_char:
            id = s.find(i)
            if s[id-1] in oper_char or s[id+1] in oper_char:
                print("输入格式错误")
                flag = False
                break
        
    return flag
                


 
def cal(x,y,opertor):
    '''加减乘除'''
    if opertor == '*':return x*y
    elif opertor == '/':return x/y
    elif opertor == '+':return x+y
    elif opertor == '-':return x-y
 
def Bottom_operation(s):
    '''无括号运算  返回一个浮点数
		symbol用于判断返回值是正还是负'''
    symbol = 0
    
    
    for c in oper_char:
        
        
        while c in s:

            id,char = (s.find(c),c)
            if c in ('*','/') and '*' in s and '/' in s:
                ids,idd = (s.find('*'),s.find('/'))
                id,char = (ids,'*') if ids <= idd else (idd,'/')
            if c in ('+','-') and '+' in s and '-' in s:
                ida,idd = (s.find('+'),s.find('-'))
                id,char = (ida,'+') if ida <= idd else (idd,'-')

                
            if id == -1:break

            
            left,right = ('','')
            for i in range(id - 1,-1,-1):
                if s[i] in oper_char:break
                left = s[i] + left
            for i in range(id + 1,len(s)):
                if s[i] in oper_char:break
                right += s[i]
           
                
            if right == '' or left == '':
                if s[0] in '-':
                    if '+' not in s[1:] and '-' not in s[1:]:break

                    s = s[1:].replace('-','负').replace('+','-').replace('负','+')
                    symbol += 1
                    continue
                
                if s[0] in '+':
                    if '+' not in s[1:] and '-' not in s[1:]:break
                    s = s[1:]
                    continue

              
            old_str = left + char + right
            new_str = str(cal(float(left),float(right),char))
            s = s.replace(old_str,new_str,1)

    if float(s) == -0.0 or float(s) == 0.0:
        return 0.0
    elif symbol % 2 == 0:
        return float(s)
    else:
        return -float(s)

 
def get_bottom(s):
    '''获取优先级最高的表达式'''
    res = re.search('\([^()]+\)',s)
    
    if res != None:
        return res.group()


 
if __name__ == '__main__':
    while True:
        s1 = input('请输入您要计算的表达式: ')
        if error(s1):
            while get_bottom(s1) != None:
                source = get_bottom(s1)
                result = Bottom_operation(format_str((source)))
                s1 = s1.replace(source,str(result))
             
            print(Bottom_operation(format_str(s1)))
        else:print("请重新输入")



