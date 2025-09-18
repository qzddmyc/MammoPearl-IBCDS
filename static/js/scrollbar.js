// 尽量在html最后引入，如需要手动调用updateScrollIndicator而提前引用，需要在最后一个修改过页面内容的的文件中使用：
// if (window.updateScrollIndicator) window.updateScrollIndicator();
// else updateScrollIndicator();

function updateScrollIndicator() {
    const thumb = document.getElementById('scroll-thumb');
    if (!thumb) return;

    // 获取页面总高度和视口高度
    const html = document.documentElement;
    const body = document.body;

    const scrollTop = html.scrollTop || body.scrollTop;
    const scrollHeight = html.scrollHeight || body.scrollHeight;
    const clientHeight = html.clientHeight || body.clientHeight;
    const indicatorContainer = document.querySelector('.scroll-indicator');
    const containerHeight = indicatorContainer.offsetHeight;

    // 计算内容可滚动的高度
    const scrollableHeight = scrollHeight - clientHeight;
    
    // 避免除以零错误
    if (scrollableHeight <= 0) {
        thumb.style.height = '100%';
        thumb.style.top = '0';
        return;
    }

    // 计算滚动百分比
    const scrollPercent = scrollTop / scrollableHeight;

    // 计算指示器高度（基于内容比例，但设置最小像素高度）
    const indicatorRatio = clientHeight / scrollHeight;
    let indicatorHeight = indicatorRatio * containerHeight;
    const minHeight = 10; // 最小高度（像素）
    indicatorHeight = Math.max(minHeight, indicatorHeight);
    
    // 计算拇指位置（考虑自身高度）
    const maxTop = containerHeight - indicatorHeight;
    const thumbTop = scrollPercent * maxTop;

    // 应用计算结果
    thumb.style.height = `${indicatorHeight}px`;
    thumb.style.top = `${thumbTop}px`;
}

// 初始化并绑定事件
document.addEventListener('DOMContentLoaded', () => {
    // 检查是否已存在滚动指示器，避免重复创建
    if (!document.querySelector('.scroll-indicator')) {
        // 创建滚动指示器元素
        const indicator = document.createElement('div');
        indicator.className = 'scroll-indicator';
        indicator.innerHTML = '<div class="scroll-indicator-thumb" id="scroll-thumb"></div>';
        document.body.appendChild(indicator);
    }

    // 更新指示器
    updateScrollIndicator();

    // 监听滚动和调整事件
    window.addEventListener('scroll', updateScrollIndicator);
    window.addEventListener('resize', updateScrollIndicator);
});