def udp_str(data:str):
    data = data[::-1] 
    data = data.upper() 

    char_count = {}  
    for i in range(26):
        char_count[chr(i + 65)] = 0
    for ch in data: 
        if ch > 'Z' or ch < 'A':
            continue 
        char_count[ch] += 1 

    char_count_sorted = dict(sorted(char_count.items(), key=lambda item: item[1], reverse=True))  
    return f'{data}, {next(iter(char_count_sorted.items()))[0]}' 
    
def tcp_str(data:str):
    data = data.lower()  
    counts = [0] * 26 
    data_out = "" 

    for ch in data:
        if ch < 'a' or ch > 'z':
            data_out = f'{data_out}{ch}' 
            continue    
        data_out = f'{data_out}{int((ord(ch) - 97) / 2)}' 
        counts[ord(ch) - 97] += 1     

    min = float('inf')  
    index = -1
    for i in range(26): 
        count = counts[i]
        if count != 0 and count <= min:
            min = count   
            index = i 
    
    return f'{data_out}, {int(index / 2)}'