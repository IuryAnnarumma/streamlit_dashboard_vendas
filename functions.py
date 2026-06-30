def formatar_numero(valor, prefixo = ''):
    for unidade in ['', 'mil', 'milhão', 'bilhão', 'trilhão']:
        if abs(valor) < 1000.0:
            if unidade in ['milhão', 'bilhão', 'trilhão'] and valor > 1.1:
                unidade = unidade.replace('ão','ões')
            
            return f'{prefixo} {valor:.2f} {unidade}'.strip()
        valor /= 1000.0
    return f'{prefixo} {valor:.2f} trilhões'.strip()