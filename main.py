import minisolvers

'''
    Function to parse and forumlate a SAT Instance object that has methods
    such as .solve and .get_model to solve the sat instance
'''
def parse_SAT(stream):
    lines = stream.readlines()
    nVars = 0
    nClauses = 0
    S = minisolvers.MinisatSolver()
    cList = []
    for line in lines:
        line = line.rstrip()
        if(line.startswith('c') or 
            line.startswith('%') or 
            line.startswith('0') or
            line == ""):
            # The current line is boilerplate code
            pass
        elif(line.startswith('p')):
            # The current line the problems definition
            line = line.split()
            nVars = int(line[2])
            nClauses = int(line[3]) 
            for i in range(nVars): 
                S.new_var()  
        else:
            # The current line is a clause
            clause = [int(x) for x in line.split() if not(x == '0')]
            cList.append(clause)
            S.add_clause(clause)
    # Return the SAT Instance
    return [S,cList]
        
'''
    Returns the UCP Matrix for the minterm
'''            
def get_ucp_matrix(m_i,cList):
    # Transforming minterm to indicate the values of the terms
    m_i = [(i+1) if m_i[i] == 1 else -(i+1) for i in range(len(m_i))]
    
    # Populating the UCP Matrix
    ucp_matrix = []
    for clause in cList:
        ucp_row = []
        for literal in m_i:
            if(literal in clause):
                ucp_row.append(1)
            else:
                ucp_row.append(0)
        ucp_matrix.append(ucp_row)
    
    return [m_i,ucp_matrix]               

'''
    Returns the cube cover given a ucp_matrix and a minterm
'''
def get_cube_cover(m_i,ucp_matrix):
    print m_i
    # Cube Cover of the given minterm
    cube_cover_I = set([])
    cube_cover = []
    
    # Marking essential literals and rows covered by them
    # TODO : Populating these sets can be parallalized
    #        Parallelize outer for loop
    
    rowsI = set()
    colsI = set()   
    for i in range(len(ucp_matrix)):
        ucp_row = ucp_matrix[i]
        if(sum(ucp_row) == 1):
            req_literal_I = ucp_row.index(1)
            colsI.add(req_literal_I)
            for j in range(len(ucp_matrix)):
                if(ucp_matrix[j][req_literal_I] == 1):
                    rowsI.add(j)
            
    # Removing essential literals and reducing matrix. Sweep stage of
    # the mark and sweep. This part needs thinking for parallelization
    
    ucp_matrix_mod = sweep(ucp_matrix,rowsI,colsI)
    
    cube_cover_I = cube_cover_I | colsI
    
    # TODO: Dominated Row and Column pruning
    # Consider ucp_matrix_mod from now on
    colsI = set([])
    rowsI = set([])
    
    
    for curIndex in range(len(ucp_matrix_mod)):
        curRow = ucp_matrix_mod[curIndex]
        for i in range(len(ucp_matrix_mod)):
            if(i != curIndex):
                examRow = ucp_matrix_mod[i]
                if(impliesRow(curRow,examRow)):
                    rowsI.add(i)
    for curIndex in range(len(ucp_matrix_mod[0])):
        for i in range(len(ucp_matrix_mod[0])):
            if(i != curIndex):
                examColIndex = i
                if(impliesCol(ucp_matrix_mod,curIndex,examColIndex)):
                    cols.add(curIndex)
      
    ucp_matrix_mod = sweep(ucp_matrix_mod,rowsI,colsI)
    
    # No need to add implied literals to cube cover          
    
    # Greedy approach to cleaning the matrix
    colSums = [0]*len(m_i)
    for i in range(len(ucp_matrix_mod)):
        for j in range(len(ucp_matrix_mod[i])):
            colSums[j] += ucp_matrix_mod[i][j]
    
    # The Mark and Sweep loop for the greedy algorithm    
    while(not(isEmpty(ucp_matrix_mod))):
    
        maxColSum = max(colSums)
        maxColSumI = colSums.index(maxColSum)
    
        colsI = set([])        
        colsI.add(maxColSumI)
        rowsI = set([])
        for i in range(len(ucp_matrix_mod)):
            for j in range(len(ucp_matrix_mod[i])):
                if(j == maxColSumI and ucp_matrix_mod[i][j] == 1):
                    rowsI.add(i)
    
        cur_ucp_matrix_mod = sweep(ucp_matrix_mod,rowsI,colsI)
        ucp_matrix_mod = cur_ucp_matrix_mod
      
    # Final Cube Cover description resolution    
    cube_cover_I = cube_cover_I | colsI
    cube_cover = [m_i[i] for i in cube_cover_I]
      
    # Returning the resulting cube cover            
    return cube_cover
                
def isEmpty(matrix):
    result = (len(matrix) == 0)
    return result
    
def sweep(ucp_matrix,rowsI,colsI):
    ucp_matrix_mod = []
    for i in range(len(ucp_matrix)):
        if(i in rowsI):
            continue
        else:
            ucp_matrix_mod.append(ucp_matrix[i])
    return ucp_matrix_mod   
    
def impliesRow(curRow,examRow):
    for i in range(len(curRow)):
        if(curRow[i] == 1):
            if(examRow[i] == 0):
                return False
    return True
    
def impliesCol(ucp_matrix_mod,curIndex,examIndex):
    for j in range(len(ucp_matrix_mod[curIndex])):
        if(ucp_matrix_mod[curIndex][j] == 1):
            if(ucp_matrix_mod[examIndex][j] == 0):
                return False
    return True      
            
'''
    Main Program for the SAT Instance algorithm
'''    
if __name__ == "__main__":
    
    # Parsing the Input in cnf form and forming a SAT Instance
    stream = open('input/input.cnf')
    [S,cList] = parse_SAT(stream)
    
    
    sat = S.solve()
    minterm = []
    if(sat): # Getting the minterm if the instance is solvable
        print "SATISFIABLE"
        minterm = list(S.get_model())
        [m_i,ucp_matrix] = get_ucp_matrix(minterm,cList)
        #print m_i
        #print ucp_matrix
        cube_cover = get_cube_cover(m_i,ucp_matrix)
        print cube_cover
    else:
        print "UNSATISFIABLE"
        
    
    
