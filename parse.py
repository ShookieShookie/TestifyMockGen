import re
import sys
import os

# filename = input('enter filename: ')
filename = 'input.txt'

f = open(filename.strip(),'r')

startLine = re.compile('.*\{')
endLine = re.compile('.*\}')

errBadName = 'errBadName'
errNoParen = 'errNoParen'
errIllegalParam = 'illegalParam'

def read_until_start(f,meaningful):
    for line in f:
        l = line.strip()
        find = startLine.search(l)
        if find:
            meaningful.append(l)
            return meaningful

def read_until_end(f,meaningful):
    for line in f:
        l = line.strip()
        end = endLine.search(l)
        if end:
            meaningful.append(l)
            break
        meaningful.append(l)



def generate_mock_type(meaningful):
    nameLineSplit = meaningful[0].split(' ')
    typeInd = -5
    InterfaceInd = -1
    for ind in range(0,len(nameLineSplit)):
        if nameLineSplit[ind] == 'type':
            typeInd = ind
        if nameLineSplit[ind] == 'interface':
            InterfaceInd = ind
    if InterfaceInd - typeInd != 2:
        return errBadName
    rawName = nameLineSplit[typeInd +1]
    mockName = 'mock' + rawName
    return mockName


def get_name_params_returns(funcDef):
    openParen = re.compile('\(')
    closeParen = re.compile('\)')
    find = openParen.search(funcDef)
    name = ""
    params = []
    returns = []
    if find:
        name = funcDef[:find.start()]
    else:
        return errNoParen + ' param open'
    close = closeParen.search(funcDef)
    if close:
        params = funcDef[find.start()+1:close.start()] # todo aware of case there is end but params blended with returns
    else:
        return errNoParen + ' param close'
    params = params.split(',')
    paramTypes = []
    for p in params:
        nameAndType = p.split(' ')        
        t = ''
        if len(nameAndType) == 1:
            t = nameAndType[0]
        elif len(nameAndType) == 2:
            t = nameAndType[1]
        else:
            return errIllegalParam
        paramTypes.append(t)
    
    returnString = funcDef[close.start()+1:].strip()
    if returnString == '':
        return name,params,returns
    openReturns = openParen.search(returnString)
    closeReturns = closeParen.search(returnString)
    if not openReturns:
        returns.append(returnString)
    elif openReturns and closeReturns:
        parenLess = returnString[1:-1]
        returns = parenLess.split(',')
    else:
        return errNoParen + ' return close'
    return name,params,returns

def generate_mock_functions(mock_name, meaningful):
    functions = meaningful[1:-1]
    functionPrints = []
    for funcDef in functions:
        lines = []
        name,params,returns = get_name_params_returns(funcDef)
        paramNames = [i.split(' ')[0] for i in params]
        paramsJoined = ','.join(params)
        joinedReturns = ''
        if len(returns) > 1:
            joinedReturns = '(' + ','.join(returns) + ')'
        else:
            joinedReturns = ','.join(returns)
        definiton = 'func (m *{}) {}({}) {} '.format(mock_name,name,paramsJoined,joinedReturns)
        definiton += '{'
        lines.append(definiton)
        shouldHaveArgs = len(returns) > 0
        calledLine = 'm.Called({})'.format(','.join(paramNames))
        returnLine = ''
        if shouldHaveArgs:
            calledLine = 'args := ' + calledLine
            returnAssert = []
            count = 0
            for r in returns:
                returnAssert.append('args.Get({}).({})'.format(count,r))
                count += 1
            returnLine = '\t return ' + ','.join(returnAssert)
        calledLine = '\t '+ calledLine
        lines.append(calledLine)
        if returnLine != '':
            lines.append(returnLine)
        lines.append('}')
        functionPrints.append(lines)
    return functionPrints

def generate_mock_def(mock_name):
    defLine = 'type {} struct'.format(mock_name) + '{'
    mock_extension = '\t mock.Mock'
    end = '}'
    return [defLine,mock_extension,end]

if __name__ == '__main__':
    meaningful = []
    meaningful = read_until_start(f,meaningful)
    read_until_end(f,meaningful)
    mock_name = generate_mock_type(meaningful)
    if mock_name == errBadName:
        print(mock_name)
        exit(0)
    mock_def = generate_mock_def(mock_name)
    for l in mock_def:
        print(l)
    mock_functions = generate_mock_functions(mock_name,meaningful)
    if mock_functions == errNoParen:
        print(mock_functions)
        exit(0)
    for func in mock_functions:
        for l in func:
            print(l)

