export function updateScrollIndicator() {
    const thumb = document.getElementById('scroll-thumb');
    if (!thumb) return;

    const html = document.documentElement;
    const body = document.body;

    const scrollTop = html.scrollTop || body.scrollTop;
    const scrollHeight = html.scrollHeight || body.scrollHeight;
    const clientHeight = html.clientHeight || body.clientHeight;
    const indicatorContainer = document.querySelector('.scroll-indicator');
    const containerHeight = indicatorContainer.offsetHeight;

    const scrollableHeight = scrollHeight - clientHeight;

    if (scrollableHeight <= 0) {
        thumb.style.height = '100%';
        thumb.style.top = '0';
        return;
    }

    const scrollPercent = scrollTop / scrollableHeight;
    const indicatorRatio = clientHeight / scrollHeight;
    let indicatorHeight = indicatorRatio * containerHeight;
    const minHeight = 10;
    indicatorHeight = Math.max(minHeight, indicatorHeight);
    const maxTop = containerHeight - indicatorHeight;
    const thumbTop = scrollPercent * maxTop;
    thumb.style.height = `${indicatorHeight}px`;
    thumb.style.top = `${thumbTop}px`;
}

!function () {
    if (!document.querySelector('.scroll-indicator')) {
        const indicator = document.createElement('div');
        indicator.className = 'scroll-indicator';
        indicator.innerHTML = '<div class="scroll-indicator-thumb" id="scroll-thumb"></div>';
        document.body.appendChild(indicator);
    }
    updateScrollIndicator();

    window.addEventListener('scroll', updateScrollIndicator);
    window.addEventListener('resize', updateScrollIndicator);
}();