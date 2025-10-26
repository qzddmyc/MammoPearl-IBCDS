// 需要在 scrollbar.js 之后引入

document.addEventListener('DOMContentLoaded', async function () {
    const qaContainer = document.querySelector('.qa-container');
    const aiQaContainer = document.querySelector('.ai-qa-container');
    const aiBtn = document.querySelectorAll('.qa-ai');
    const normalBtn = document.querySelectorAll('.qa-normal');
    const addConversationBtn = document.querySelector('.add-conversation-btn');
    const questionInputContainer = document.querySelector('.question-input-container');
    const cancelBtn = document.querySelector('.cancel-btn');
    const pageTitle = document.querySelector('.page-title h1');
    const textarea = document.querySelector('.question-input');

    const initialPageTitle = pageTitle.innerHTML;
    let observer = null;    // normal-observer
    let observerAI = null;  // ai-observer

    let isQuerying = false; // 判断当前是否正在发送fetch请求, 防止阻塞
    const SEP = 2000;       // 查询间隔

    let DISABLE_INTERACTION = DISABLE_INTERACTION_global;
    async function check_connection() {
        try {
            const response = await fetch('api/check_conn', {
                method: 'POST',
                body: 'hello',
                headers: {
                    'Content-Type': 'text/plain'
                }
            });
            const result = await response.json();
            if (result.success) {
                return true;
            }
            return false;
        } catch (error) {
            return false;
        }
    }
    if (!DISABLE_INTERACTION) {
        const res = await check_connection();
        if (res) {
            console.log("服务器连接成功");
        } else {
            alert("请使用 python app.py 开启服务器。");
            console.warn("Warning: 服务器连接失败");
            DISABLE_INTERACTION = true;
        }
    }

    /**
     * 存在unresolved messages时调用该函数即可
     * 在调用之前，需要确保存在一个id="unresolved"的<div class="ai-qa-item answer-item">标签，
     * 该标签中的内容允许为任意值，之后会将这个标签初始化为等待回答状态。
     * 当然，在该过程退出后，会清除div元素的id信息
     * 调用此函数时，会自动将文本域隐藏，并禁用“添加对话”按钮。询问过程结束后，会自动解除该按钮的禁用
     */
    function touchingReply() {
        if (!questionInputContainer.classList.contains('hide')) hideQuestionInput();
        addConversationBtn.disabled = true;

        const div = document.getElementById('unresolved');
        const p = div.querySelector('p');
        let queryTimer = null;

        p.innerHTML = `<span>等待AI回复中</span><span id="loading-dots"></span>`;
        const loadingStrings = [".", "..", "...", "....", ".....", "......"];
        const loadingTyper = new Typed('#unresolved p span#loading-dots', {
            strings: loadingStrings,
            typeSpeed: 0,
            backSpeed: 0,
            backDelay: 1000,
            loop: true,
            showCursor: false,
        });

        /**
         * 清除持续发送请求的定时器，清除打字机效果，修改p元素(应答元素)内容，清除应答元素的id，解除按钮禁用
         * @param {string} s 让p元素展示的新字符串。若为null，则不进行修改。
         * @param {boolean} clearID 是否清除div的id值
         */
        function clearAllRequestAndShowNewMessage(s, clearID = true) {
            if (queryTimer) {
                clearInterval(queryTimer);
            }
            if (loadingTyper) {
                loadingTyper.destroy();
            }
            if (s) { p.innerHTML = s; }
            if (clearID) {
                div.id = null;
            }
            addConversationBtn.disabled = false;
        }

        queryTimer = setInterval(async () => {
            if (isQuerying) return;
            isQuerying = true;
            try {
                const response = await fetch('api/get_status');
                const result = await response.json();
                if (result.error) {
                    clearAllRequestAndShowNewMessage(`fatal error: ${result.message}`);
                }
                if (result.resolve) {
                    clearAllRequestAndShowNewMessage('');
                    const options = {
                        strings: [result.message],
                        typeSpeed: 20,
                        showCursor: false,
                        loop: false,
                        onComplete: function (typed) {
                            typed.destroy();
                            p.innerHTML = result.message;
                        }
                    };
                    new Typed(p, options);
                    console.log('AI完成了回答。');
                } else {
                    console.log('请求成功，但AI未完成回答。');
                }
            } catch (error) {
                console.error('fetch 请求(api/get_status)失败', error);
                clearAllRequestAndShowNewMessage('请求发生错误：' + error);
            }
            isQuerying = false;
        }, SEP);
    }

    async function initAIQAs() {
        let ai_qas = [];
        let contianUnresolved = false;
        if (!DISABLE_INTERACTION) {
            try {
                const response = await fetch('api/get_full_json');
                const result = await response.json();
                if (!result.success) {
                    alert("获取初始问答列表失败: " + result.data);
                } else {
                    ai_qas = result.data;
                    contianUnresolved = result.unresolved;
                }
            } catch (error) {
                alert("获取初始问答列表失败: ", error);
            }
        }
        ai_qas = Array.from(ai_qas).filter(each => each.flag !== Flags.wrong);
        let html = '';
        if (ai_qas.length === 0) {
            if (DISABLE_INTERACTION) html += '<h3>未能连接服务器，当前页面仅作展示</h3>';
            else html += '<h3>暂无内容，请点击“添加对话”进行添加</h3>';
        }
        ai_qas.forEach(qa => {
            html += `
                <div class="ai-qa-item question-item">
                    <div class="ai-question">
                        <div class="message-content">
                            <p>${qa.ask}</p>
                        </div>
                    </div>
                    <div class="ai-avatar ai-q-avatar">You</div>
                </div>

                <div class="ai-qa-item answer-item"${qa.flag === Flags.unresolved ? ' id="unresolved"' : ''}>
                    <div class="ai-avatar ai-a-avatar">AI</div>
                    <div class="ai-answer">
                        <div class="message-content">
                            <p>${qa.reply}</p>
                        </div>
                    </div>
                </div>
            `;
        });
        if (addConversationBtn) {
            addConversationBtn.insertAdjacentHTML('afterend', html);
        } else {
            aiQaContainer.innerHTML = html;
        }
        initAIQaAnimation();
        if (contianUnresolved) {
            touchingReply();
        };

        if (!DISABLE_INTERACTION) {
            const response = await fetch('api/check_api_environ');
            const result = await response.json();
            if (!result.exist) {
                alert("用户api key未配置，无法使用AI功能");
                DISABLE_INTERACTION = true;
            } else {
                console.log("检测api配置成功");
            }
        }
        if (DISABLE_INTERACTION) addConversationBtn.disabled = true;
    }

    function initAIQaAnimation() {
        const aiQaItems = Array.from(document.querySelectorAll('.ai-qa-item'));
        const observerOptions = {
            root: null,
            rootMargin: '0px 0px 100px 0px',
            threshold: 0.1
        };

        if (observerAI) {
            observerAI.disconnect();
            observerAI = null;
        }

        observerAI = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !entry.target.classList.contains('visible')) {
                    const index = aiQaItems.indexOf(entry.target);
                    setTimeout(() => {
                        entry.target.classList.add('visible');
                    }, index * 50);
                    observerAI.unobserve(entry.target);
                }
            });
        }, observerOptions);

        aiQaItems.forEach(item => {
            observerAI.observe(item);
        });
    }

    function initNormalQaAnimation() {
        const qaItems = Array.from(document.querySelectorAll('.qa-item'));
        const observerOptions = {
            root: null,
            rootMargin: '0px 0px 100px 0px',
            threshold: 0.1
        };

        if (observer) {
            observer.disconnect();
            observer = null;
        }

        observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !entry.target.classList.contains('visible')) {
                    const index = qaItems.indexOf(entry.target);
                    setTimeout(() => {
                        entry.target.classList.add('visible');
                    }, index * 50);
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        qaItems.forEach(item => {
            observer.observe(item);
        });
    }

    function switchToAIQA() {
        qaContainer.classList.add('hide');
        aiQaContainer.classList.remove('hide');

        aiBtn.forEach(e => e.classList.add('hide'));
        normalBtn.forEach(e => e.classList.remove('hide'));
        pageTitle.innerHTML = 'AI 解答';

        document.querySelectorAll('.ai-qa-item').forEach(item => {
            item.classList.remove('visible');
        });

        initAIQaAnimation();
        if (window.updateScrollIndicator) window.updateScrollIndicator();
        else updateScrollIndicator();
    }

    function switchToNormalQA() {
        aiQaContainer.classList.add('hide');
        qaContainer.classList.remove('hide');

        normalBtn.forEach(e => e.classList.add('hide'));
        aiBtn.forEach(e => e.classList.remove('hide'));
        pageTitle.innerHTML = initialPageTitle;

        questionInputContainer.classList.add('hide');

        document.querySelectorAll('.qa-item').forEach(item => {
            item.classList.remove('visible');
        });
        initNormalQaAnimation();

        if (window.updateScrollIndicator) window.updateScrollIndicator();
        else updateScrollIndicator();
    }

    function showQuestionInput() {
        questionInputContainer.classList.remove('hide');
        addConversationBtn.disabled = true;
    }

    function hideQuestionInput() {
        questionInputContainer.classList.add('hide');
        textarea.value = '';
        addConversationBtn.disabled = false;
    }

    if (aiBtn) aiBtn.forEach(e => e.addEventListener('click', switchToAIQA));
    if (normalBtn) normalBtn.forEach(e => e.addEventListener('click', switchToNormalQA));
    if (addConversationBtn) addConversationBtn.addEventListener('click', showQuestionInput);
    if (cancelBtn) cancelBtn.addEventListener('click', hideQuestionInput);

    const submitToAI = async function () {
        const usrInput = textarea.value.trim();
        if (!usrInput) {
            alert("请输入内容后提交");
            return;
        };
        async function sendUsrIptToAI(msg) {
            try {
                const response = await fetch('api/send_msg_to_ai', {
                    method: 'POST',
                    body: msg,
                    headers: {
                        'Content-Type': 'text/plain'
                    }
                });
                const result = await response.json();
                return {
                    success: result.success,
                    data: result.data,
                }

            } catch (error) {
                return {
                    success: false,
                    data: error
                };
            }
        }
        const reply = await sendUsrIptToAI(usrInput);
        if (reply.success) {
            hideQuestionInput();
            html = `
                <div class="ai-qa-item question-item visible">
                    <div class="ai-question">
                        <div class="message-content">
                            <p>${usrInput}</p>
                        </div>
                    </div>
                    <div class="ai-avatar ai-q-avatar">You</div>
                </div>

                <div class="ai-qa-item answer-item visible" id="unresolved">
                    <div class="ai-avatar ai-a-avatar">AI</div>
                    <div class="ai-answer">
                        <div class="message-content">
                            <p></p>
                        </div>
                    </div>
                </div>
            `;
            addConversationBtn.insertAdjacentHTML('afterend', html);
            touchingReply();
        } else {
            alert(`AI请求失败：${reply.data}`);
        }
    }

    document.getElementById('ai-confirm-btn').addEventListener('click', function (e) {
        e.preventDefault();
        submitToAI();
    });
    textarea.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey && !e.ctrlKey) {
            e.preventDefault();
            submitToAI();
        }
    });

    await initAIQAs();
    initNormalQaAnimation();
});