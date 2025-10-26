// 页面切换时使用的过渡背景，现在不再使用

document.addEventListener('DOMContentLoaded', function () {
    const doms = {
        loading: document.querySelector('.loading'),
    }
    const shouldShowLoading = false;    // 从后端获取（根据session/localStorage判断是否首次进入）
    if (!shouldShowLoading) {
        const transition = getComputedStyle(doms.loading).transition;
        doms.loading.style.transition = 'none';
        
        doms.loading.classList.remove('show');
        doms.loading.clientHeight;  // reflow
        doms.loading.style.transition = transition;
    } else {
        setTimeout(function () {
            doms.loading.classList.remove('show');
        }, 500);
    }
});

/** 
 *  用法：在页面中加入以下元素。
 * 
    <!-- 加载界面 -->
    <div class="loading show">
        <!-- 网格背景 -->
        <div class="grid-bg"></div>

        <!-- 装饰元素 -->
        <div class="decor-element circle circle1"></div>
        <div class="decor-element circle circle2"></div>
        <div class="decor-element circle circle3"></div>
        <div class="decor-element circle circle4"></div>

        <!-- 随机角度斜线 -->
        <div class="decor-element line line1"></div>
        <div class="decor-element line line2"></div>
        <div class="decor-element line line3"></div>
        <div class="decor-element line line4"></div>
        <div class="decor-element line line5"></div>
        <div class="decor-element line line6"></div>

        <!-- 随机点 -->
        <div class="dot dot1"></div>
        <div class="dot dot2"></div>
        <div class="dot dot3"></div>
        <div class="dot dot4"></div>
        <div class="dot dot5"></div>
        <div class="dot dot6"></div>
        <div class="dot dot7"></div>
        <div class="dot dot8"></div>
        <div class="dot dot9"></div>
        <div class="dot dot10"></div>
        <div class="dot dot11"></div>
        <div class="dot dot12"></div>
        <div class="dot dot13"></div>
        <div class="dot dot14"></div>
        <div class="dot dot15"></div>
        <div class="dot dot16"></div>
        <div class="dot dot17"></div>
        <div class="dot dot18"></div>
        <div class="dot dot19"></div>
        <div class="dot dot20"></div>
        <div class="dot dot21"></div>
        <div class="dot dot22"></div>
        <div class="dot dot23"></div>
        <div class="dot dot24"></div>
        <div class="dot dot25"></div>
        <div class="dot dot26"></div>
        <div class="dot dot27"></div>
        <div class="dot dot28"></div>
        <div class="dot dot29"></div>
        <div class="dot dot30"></div>
        <div class="dot dot31"></div>
        <div class="dot dot32"></div>
        <div class="dot dot33"></div>
        <div class="dot dot34"></div>
        <div class="dot dot35"></div>
    </div>
*/