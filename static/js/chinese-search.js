// 中文搜索支持 - 使用 lunr-languages 进行中文分词
// 替换 Zola 默认的 elasticlunr.js

(function() {
    // 动态加载 lunr.js 和 lunr-languages
    const loadScript = (src) => {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    };

    async function initSearch() {
        try {
            // 加载 lunr.js
            await loadScript('https://cdn.jsdelivr.net/npm/lunr@2.3.9/lunr.min.js');
            
            // 加载 lunr-languages 中文支持
            await loadScript('https://cdn.jsdelivr.net/npm/lunr-languages@1.14.0/lunr.stemmer.support.min.js');
            await loadScript('https://cdn.jsdelivr.net/npm/lunr-languages@1.14.0/lunr.zh.min.js');
            
            // 加载 Zola 生成的搜索索引
            const response = await fetch('{{ get_url(path="search_index.zh.js") }}');
            const searchIndex = await response.json();
            
            // 构建索引（使用中文分词）
            const index = lunr(function() {
                this.use(lunr.zh); // 使用中文分词
                
                this.ref('id');
                this.field('title', { boost: 10 });
                this.field('description');
                this.field('content');
                this.field('path');
                
                searchIndex.forEach((doc, idx) => {
                    this.add({
                        id: idx,
                        title: doc.title,
                        description: doc.description,
                        content: doc.content,
                        path: doc.path
                    });
                });
            });
            
            // 绑定搜索功能
            bindSearch(index);
            
        } catch (error) {
            console.error('搜索初始化失败:', error);
        }
    }

    function bindSearch(index) {
        const searchInput = document.getElementById('search-input');
        const searchResults = document.getElementById('search-results');
        
        if (!searchInput || !searchResults) return;
        
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            
            if (query.length === 0) {
                searchResults.innerHTML = '';
                searchResults.style.display = 'none';
                return;
            }
            
            // 中文搜索：支持单字匹配
            const results = index.search(query);
            
            if (results.length === 0) {
                searchResults.innerHTML = '<li class="no-results">未找到相关结果</li>';
            } else {
                searchResults.innerHTML = results.map(result => {
                    const doc = searchIndex[result.ref];
                    return `
                        <li class="search-result">
                            <a href="${doc.path}">
                                <h4>${highlightMatch(doc.title, query)}</h4>
                                ${doc.description ? `<p>${highlightMatch(doc.description, query)}</p>` : ''}
                            </a>
                        </li>
                    `;
                }).join('');
            }
            
            searchResults.style.display = 'block';
        });
        
        // 点击外部关闭搜索结果
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.search-container')) {
                searchResults.style.display = 'none';
            }
        });
    }

    function highlightMatch(text, query) {
        if (!text) return '';
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    // 页面加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSearch);
    } else {
        initSearch();
    }
})();
