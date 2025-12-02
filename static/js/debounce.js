/**
 * 防抖函数
 * @param {Function} func - 需要防抖的处理函数
 * @param {number} delay - 延迟时间（毫秒），事件停止触发后等待该时间才执行函数
 * @returns {Function} 包装后的防抖函数
 */
function debounce(func, delay) {
    let timer = null;
    return function (...args) {
        if (timer) clearTimeout(timer);
        timer = setTimeout(() => {
            func.apply(this, args);
        }, delay);
    };
}