// Mermaid 流程图支持
// 自动渲染所有 class="mermaid" 的代码块

document.addEventListener('DOMContentLoaded', function() {
    // 查找所有 mermaid 代码块
    const mermaidBlocks = document.querySelectorAll('pre code.language-mermaid');
    
    if (mermaidBlocks.length === 0) return;
    
    // 动态加载 Mermaid
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js';
    script.onload = function() {
        mermaid.initialize({
            startOnLoad: false,
            theme: 'default',
            securityLevel: 'loose',
            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        });
        
        // 逐个渲染 mermaid 代码块
        mermaidBlocks.forEach((block, index) => {
            const pre = block.parentElement;
            const code = block.textContent.trim();
            
            // 创建容器
            const container = document.createElement('div');
            container.className = 'mermaid-container';
            container.id = `mermaid-${index}`;
            
            // 替换 pre 标签
            pre.parentElement.insertBefore(container, pre);
            pre.remove();
            
            // 渲染图表
            try {
                mermaid.render(`mermaid-${index}`, code).then(({ svg }) => {
                    container.innerHTML = svg;
                });
            } catch (e) {
                container.innerHTML = `<div class="mermaid-error">Mermaid 渲染失败：${e.message}</div>`;
            }
        });
    };
    document.head.appendChild(script);
});
