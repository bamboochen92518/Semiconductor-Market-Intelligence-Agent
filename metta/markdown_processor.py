import re

class MarkdownProcessor:
    """處理 Markdown 格式，專門用於郵件 HTML 轉換"""
    
    def __init__(self):
        pass
    
    def process_for_html_chat(self, markdown_text: str) -> str:
        """將 Markdown 轉換為 HTML 格式（用於郵件）"""
        if not markdown_text:
            return ""
        
        text = markdown_text
        
        # 1. 處理特殊的 SECTOR OVERVIEW 格式
        text = self._process_sector_overview(text)
        
        # 2. 處理特殊的 MONITORING STATUS 格式
        text = self._process_monitoring_status(text)
        
        # 3. 處理 Markdown 表格
        text = self._process_markdown_tables(text)
        
        # 4. 處理粗體 **text** -> <b>text</b>
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        
        # 5. 處理斜體 *text* -> <i>text</i>
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        
        # 6. 處理標題 (包括 === 格式和 ####)
        text = re.sub(r'^=== (.*?) ===', r'<h3 style="color: #2E86AB; border-bottom: 1px solid #ddd; padding-bottom: 5px;">\1</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^#### (.*)', r'<h4 style="color: #495057; margin: 15px 0 10px 0;">\1</h4>', text, flags=re.MULTILINE)
        text = re.sub(r'^### (.*)', r'<h3 style="color: #495057; margin: 20px 0 15px 0;">\1</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.*)', r'<h2 style="color: #343a40; margin: 25px 0 20px 0;">\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.*)', r'<h1 style="color: #212529; margin: 30px 0 25px 0;">\1</h1>', text, flags=re.MULTILINE)
        
        # 7. 處理列表項 - text -> <li>text</li>
        text = re.sub(r'^- (.*)', r'<li style="margin: 5px 0;">\1</li>', text, flags=re.MULTILINE)
        
        # 8. 處理代碼塊
        text = re.sub(r'```(.*?)```', r'<pre style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; border: 1px solid #e9ecef; overflow-x: auto;"><code>\1</code></pre>', text, flags=re.DOTALL)
        text = re.sub(r'`(.*?)`', r'<code style="background-color: #f8f9fa; padding: 2px 4px; border-radius: 3px; font-family: monospace; font-size: 90%;">\1</code>', text)
        
        # 9. 處理鏈接
        text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2" style="color: #007bff; text-decoration: none;">\1</a>', text)
        
        # 10. 處理表格格式的股價數據
        text = self._process_stock_table(text)
        
        # 11. 處理換行
        text = re.sub(r'\n\n+', '</p><p>', text)
        text = f'<p>{text}</p>'
        
        # 12. 清理空的段落
        text = re.sub(r'<p></p>', '', text)
        text = re.sub(r'<p>\s*</p>', '', text)
        
        # 13. 確保 $ 符號正確顯示
        text = text.replace('\\$', '$')
        
        return text.strip()
    
    def _process_sector_overview(self, text: str) -> str:
        """處理 SECTOR OVERVIEW 部分，轉換為美觀的列表格式"""
        # 匹配整個 SECTOR OVERVIEW 區塊
        pattern = r'=== SECTOR OVERVIEW ===\s*Sector Average: ([+-]?\d+\.\d+%)\s*Companies Tracked: (\d+)\s*Individual Stock Performance:\s*-+\s*(.*?)(?=\n\n=== |$)'
        
        match = re.search(pattern, text, re.DOTALL)
        if match:
            sector_avg = match.group(1)
            companies_count = match.group(2)
            stock_data = match.group(3).strip()
            
            # 解析個股數據
            stock_lines = [line.strip() for line in stock_data.split('\n') if line.strip()]
            
            # 建立美觀的 HTML 格式
            html_replacement = f"""=== SECTOR OVERVIEW ===

<div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
    <h4 style="color: #495057; margin-top: 0;">📊 Market Summary</h4>
    <ul style="list-style: none; padding: 0;">
        <li style="padding: 5px 0;"><b>Sector Average:</b> <span style="color: {'green' if '+' in sector_avg else 'red'}; font-weight: bold;">{sector_avg}</span></li>
        <li style="padding: 5px 0;"><b>Companies Tracked:</b> {companies_count}</li>
    </ul>
</div>

<div style="background-color: #fff; border: 1px solid #dee2e6; border-radius: 8px; margin: 10px 0;">
    <h4 style="color: #495057; margin: 0; padding: 15px; background-color: #f8f9fa; border-bottom: 1px solid #dee2e6; border-radius: 8px 8px 0 0;">💹 Individual Stock Performance</h4>
    <table style="width: 100%; border-collapse: collapse;">
        <thead>
            <tr style="background-color: #f1f3f4;">
                <th style="padding: 10px; text-align: left; border-bottom: 1px solid #dee2e6;">Company</th>
                <th style="padding: 10px; text-align: left; border-bottom: 1px solid #dee2e6;">Symbol</th>
                <th style="padding: 10px; text-align: right; border-bottom: 1px solid #dee2e6;">Price</th>
                <th style="padding: 10px; text-align: right; border-bottom: 1px solid #dee2e6;">Change</th>
            </tr>
        </thead>
        <tbody>"""
            
            # 解析每行股價數據
            for line in stock_lines:
                # 匹配格式: "NVIDIA (NVDA): $ 178.94 ( -0.94%)"
                stock_match = re.search(r'(\w+(?:\s+\w+)*)\s*\((\w+)\):\s*\$\s*([\d.]+)\s*\(\s*([+-]?\d+\.\d+%)\)', line)
                if stock_match:
                    company = stock_match.group(1).strip()
                    symbol = stock_match.group(2).strip()
                    price = stock_match.group(3).strip()
                    change = stock_match.group(4).strip()
                    
                    change_color = 'green' if '+' in change else 'red'
                    
                    html_replacement += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #f1f3f4;">{company}</td>
                <td style="padding: 8px; border-bottom: 1px solid #f1f3f4; font-family: monospace;">{symbol}</td>
                <td style="padding: 8px; text-align: right; border-bottom: 1px solid #f1f3f4; font-family: monospace;">${price}</td>
                <td style="padding: 8px; text-align: right; border-bottom: 1px solid #f1f3f4; color: {change_color}; font-weight: bold;">{change}</td>
            </tr>"""
            
            html_replacement += """
        </tbody>
    </table>
</div>"""
            
            text = text.replace(match.group(0), html_replacement)
        
        return text
    
    def _process_monitoring_status(self, text: str) -> str:
        """處理 MONITORING STATUS 部分，轉換為美觀的列表格式"""
        # 匹配 MONITORING STATUS 區塊
        pattern = r'=== MONITORING STATUS ===\s*Volatility Thresholds: ([^\\n]+)\s*Next Report: ([^\\n]+)'
        
        match = re.search(pattern, text)
        if match:
            thresholds = match.group(1).strip()
            next_report = match.group(2).strip()
            
            html_replacement = f"""=== MONITORING STATUS ===

<div style="background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #2196f3;">
    <h4 style="color: #1976d2; margin-top: 0;">⚙️ System Configuration</h4>
    <ul style="list-style: none; padding: 0;">
        <li style="padding: 5px 0;"><b>🚨 Volatility Thresholds:</b> {thresholds}</li>
        <li style="padding: 5px 0;"><b>⏰ Next Report:</b> {next_report}</li>
        <li style="padding: 5px 0;"><b>📊 Monitoring Frequency:</b> Every 15 minutes</li>
        <li style="padding: 5px 0;"><b>🔄 Status:</b> <span style="color: green; font-weight: bold;">Active</span></li>
    </ul>
</div>"""
            
            text = text.replace(match.group(0), html_replacement)
        
        return text
    
    def _process_stock_table(self, text: str) -> str:
        """處理其他可能的表格格式股價數據"""
        # 處理用破折號分隔的內容
        text = re.sub(r'^-{20,}$', '<hr style="border: 1px solid #dee2e6; margin: 15px 0;">', text, flags=re.MULTILINE)
        
        return text

    def _process_markdown_tables(self, text: str) -> str:
        """處理標準 Markdown 表格格式"""
        # 匹配 Markdown 表格格式
        # | Header 1 | Header 2 | Header 3 |
        # |----------|----------|----------|
        # | Cell 1   | Cell 2   | Cell 3   |
        
        table_pattern = r'(\|[^\n]+\|\n\|[-:\s|]+\|\n(?:\|[^\n]+\|\n?)+)'
        
        def convert_table(match):
            table_text = match.group(1).strip()
            lines = [line.strip() for line in table_text.split('\n') if line.strip()]
            
            if len(lines) < 3:  # 至少需要標題、分隔符、一行數據
                return table_text
            
            html_table = '<table style="width: 100%; border-collapse: collapse; margin: 15px 0; border: 1px solid #dee2e6;">\n'
            
            # 處理標題行
            header_line = lines[0]
            header_cells = [cell.strip() for cell in header_line.split('|')[1:-1]]  # 移除開頭和結尾的空字符串
            
            html_table += '  <thead>\n    <tr style="background-color: #f8f9fa;">\n'
            for cell in header_cells:
                html_table += f'      <th style="padding: 12px; text-align: left; border: 1px solid #dee2e6; font-weight: bold;">{cell}</th>\n'
            html_table += '    </tr>\n  </thead>\n'
            
            # 處理數據行
            html_table += '  <tbody>\n'
            for line in lines[2:]:  # 跳過標題和分隔符行
                if '|' in line:
                    cells = [cell.strip() for cell in line.split('|')[1:-1]]
                    html_table += '    <tr>\n'
                    for i, cell in enumerate(cells):
                        # 檢查是否為數字或百分比，如果是則右對齊
                        text_align = 'right' if re.match(r'^[+-]?\d+\.?\d*%?$', cell.strip()) else 'left'
                        
                        # 檢查是否為股價變化，添加顏色
                        cell_style = f'padding: 10px; text-align: {text_align}; border: 1px solid #dee2e6;'
                        if '%' in cell and ('+' in cell or '-' in cell):
                            color = 'green' if '+' in cell else 'red'
                            cell_style += f' color: {color}; font-weight: bold;'
                        
                        html_table += f'      <td style="{cell_style}">{cell}</td>\n'
                    html_table += '    </tr>\n'
            
            html_table += '  </tbody>\n</table>'
            return html_table
        
        # 替換所有找到的表格
        text = re.sub(table_pattern, convert_table, text, flags=re.MULTILINE)
        
        return text

# 全局實例
markdown_processor = MarkdownProcessor()