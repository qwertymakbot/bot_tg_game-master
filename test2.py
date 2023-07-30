import os
clas = '11 класс'
"""with open('0.txt', 'r', encoding='utf-8') as f:
    print(f.readlines())
    quit()"""



def is_part_in_list(str_, list):
    for word in list:
        if word in str_:
            return word
    return False


data = ['10.', '11.', '12.', '13.', '14.', '15.', '16.', '17.', '18.', '19.', '20.', '21.', '22.', '23.', '24.', '25.', '26.', '27.', '28.', '29.', '30.', '31.', '32.', '33.', '34.', '35.', '36.', '37.', '38.', '39.','1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.']
letters = ['А)', 'Б)', 'В)', 'Г)', 'а)', 'б)', 'в)', 'г)', 'а)', 'б) ', 'в) ', 'г) ', '1)', '2)', '3)', '4)', 'a)']
with open('test.txt', 'r', encoding='utf-8') as f:
    data_test = []
    text = f.readlines()
    f.close()
    count = 1
    lines = []
    one_line = []
    answer = []
    for string in text:
        num = is_part_in_list(string, data)
        if num:
            if len(lines) == 3:
                with open(f'res/education/{clas}/prac/{count}.txt', 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                    f.close()
                    count +=1
                    lines.clear()
            if one_line:
                for ans in answer:
                    if '+' in ans:
                        one_line.append(ans.replace('+','').strip().rstrip()+':')
                        answer.remove(ans)
                for ans in answer:
                    one_line.append(f'{ans.strip().rstrip()}.')
                one_line.append(one_line.pop(-1).replace('.',''))
                lines.append(''.join(one_line))
                one_line.clear()
                answer.clear()

            one_line.append(string.replace(num,'').replace(':','').replace('тест-','').replace('тест','').strip().rstrip() + ':')
        else:
            leter = is_part_in_list(string, letters)
            if leter:
                answer.append(string.replace(leter, '').strip().rstrip())
print('good')

