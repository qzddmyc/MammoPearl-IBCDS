/**
 * 防抖函数
 * @param {Function} func - 需要防抖的处理函数
 * @param {number} delay - 延迟时间（毫秒），事件停止触发后等待该时间才执行函数
 * @returns {Function} 包装后的防抖函数
 */
function debounce(func, delay) {
    let timer = null; // 用于保存定时器ID
    return function (...args) {
        // 每次触发事件时，清除上一个定时器
        if (timer) clearTimeout(timer);
        // 重新设置定时器，延迟执行处理函数
        timer = setTimeout(() => {
            func.apply(this, args); // 确保this指向正确（指向触发事件的元素）
        }, delay);
    };
}