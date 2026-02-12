import { DISABLE_INTERACTION_global, LocalStorage_DataName } from "./data/vars.js";

!async function () {
    const dropArea = document.getElementById('drop-area');              // 整个虚线框内的内容
    const fileInput = document.getElementById('image-upload');          // 表单中的input.file元素
    const previewImage = document.getElementById('preview-image');      // 图片预览区的img标签; 使用base64展示图片
    const imagePreview = document.getElementById('image-preview');      // 图片的预览区域-存在图片时展示, 在image-preview-container内
    const noImageState = document.getElementById('no-image-state');     // 图片的预览区域-无图片时展示, 在image-preview-container内
    const removeImage = document.getElementById('remove-image');        // 删除已上传图片的按钮
    const imageFilename = document.getElementById('image-filename');    // 展示图片名称的区域, 是h4
    const uploadBtn = document.getElementById('upload-btn');            // "选择图片"按钮
    const submitBtn = document.getElementById('submit-btn');            // "提交"按钮
    const errorModal = document.getElementById('error-modal');
    const errorMessage = document.getElementById('error-message');
    const closeErrorBtn = document.getElementById('close-error');

    let __info = null;
    let removeImgWhenErrorModalClosed = false;

    let DISABLE_INTERACTION = DISABLE_INTERACTION_global;

    async function check_connection() {
        try {
            const response = await fetch('/api/check_conn', {
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

    let countdownTimer = null;
    const countdownTime = 5;
    let countdownSeconds = countdownTime;
    const originalBtnText = closeErrorBtn.textContent || "确定";

    function handleFileUpload(files, isManual = false) {
        if (files.length > 0) {
            const file = files[0];
            const validTypes = ['image/jpg', 'image/jpeg', 'image/png'];
            if (validTypes.includes(file.type)) {
                if (!isManual) {
                    setFileInputValue(fileInput, file);
                }
                imageFilename.textContent = file.name;
                imageFilename.classList.remove('placeholder');

                const reader = new FileReader();
                reader.onload = function (e) {
                    previewImage.src = e.target.result;
                    imagePreview.style.display = 'block';
                    noImageState.style.display = 'none';
                    dropArea.classList.add('border-success');
                    dropArea.classList.remove('border-dashed', 'drag-over');
                }
                reader.readAsDataURL(file);
            } else {
                showErrorModal('请上传JPG、JPEG或PNG格式的图片！');
                dropArea.classList.remove('drag-over');
            }
        }
    }

    function setFileInputValue(input, file) {
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        input.files = dataTransfer.files;
        const event = new Event('change', { bubbles: true });
        event.isManual = true;
        input.dispatchEvent(event);
    }

    function showErrorModal(message) {
        errorMessage.textContent = message;
        errorModal.classList.add('active');
        countdownSeconds = countdownTime;
        updateCountdown();
        countdownTimer = setInterval(() => {
            countdownSeconds--;
            updateCountdown();
            if (countdownSeconds <= 0) {
                clearInterval(countdownTimer);
                closeErrorModal();
            }
        }, 1000);
    }

    function updateCountdown() {
        closeErrorBtn.textContent = `${originalBtnText}(${countdownSeconds})`;
    }

    function closeErrorModal() {
        if (removeImgWhenErrorModalClosed) {
            removeImage.click();
            removeImgWhenErrorModalClosed = false;
        }
        errorModal.classList.remove('active');
        clearInterval(countdownTimer);
        closeErrorBtn.textContent = originalBtnText;
    }

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, function () {
            dropArea.classList.add('drag-over');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, function () {
            dropArea.classList.remove('drag-over');
        }, false);
    });

    dropArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFileUpload(files);
    }

    uploadBtn.addEventListener('click', function () {
        fileInput.click();
    });

    fileInput.addEventListener('change', function (e) {
        const isManual = e.isManual || false;
        handleFileUpload(this.files, isManual);
    });

    removeImage.addEventListener('click', function () {
        previewImage.src = '';
        imagePreview.style.display = 'none';
        noImageState.style.display = 'block';
        dropArea.classList.remove('border-success');
        dropArea.classList.add('border-dashed');
        fileInput.value = '';
        imageFilename.textContent = '传入图片后显示图片名...';
        imageFilename.classList.add('placeholder');
    });

    closeErrorBtn.addEventListener('click', closeErrorModal);

    errorModal.addEventListener('click', function (e) {
        // close error modal when click the margin
        if (e.target === errorModal) {
            closeErrorModal();
        }
    });

    submitBtn.addEventListener('click', async function () {
        if (fileInput.files.length > 0) {
            if (DISABLE_INTERACTION) {
                alert("提示：当前环境仅展示页面，无法提交数据。");
                return;
            }

            const formData = new FormData();

            const file = fileInput.files[0];
            const MAX_FILE_SIZE = 20 * 1024 * 1024;

            if (file.size > MAX_FILE_SIZE) {
                showErrorModal('文件过大，请上传小于 20MB 的文件。');
                removeImgWhenErrorModalClosed = true;
                return;
            }

            formData.append('image_data', file, file.name);

            const usrToken = localStorage.getItem(LocalStorage_DataName);
            if (usrToken) formData.append('usrToken', usrToken);

            try {
                const response = await fetch('/api/v1', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    const res_A = result.RES_TF;
                    const res_B = result.RES_ACC;
                    if (__info) {
                        console.error("__info did not cleared!");
                    }
                    __info = {
                        relative_path: result.relative_dir_path,
                    }
                    showResultModal(res_A, res_B);
                } else {
                    console.log(result.message);
                    alert('发生错误：' + result.message);
                    removeImage.click();
                }
            } catch (error) {
                console.error('错误:', error);
                alert('错误：' + error);
                removeImage.click();
            }

        } else {
            dropArea.classList.add('shake');
            setTimeout(() => {
                dropArea.classList.remove('shake');
            }, 1200);
            return;
        }
    });

    const resultModal = document.getElementById('result-modal');
    const detectionResult = document.getElementById('detection-result');
    const detectionConfidence = document.getElementById('detection-confidence');
    const detections = document.querySelectorAll('.result-item span');  // includes detectionResult and detectionConfidence
    const openMdBtn = document.getElementById('open-md');
    const openTxtBtn = document.getElementById('open-txt');
    const closeResultBtn = document.getElementById('close-result');

    function showResultModal(result, confidence) {
        detectionResult.textContent = result;
        detectionConfidence.textContent = confidence;
        if (result === '阴性') {
            detections.forEach(item => {
                item.classList.remove('bad');
            })
        } else {
            detections.forEach(item => {
                item.classList.add('bad');
            })
        }
        resultModal.classList.add('active');
    }

    function closeResultModal() {
        __info = null;
        removeImage.click();
        resultModal.classList.remove('active');
    }

    openMdBtn.addEventListener('click', async function () {
        await open_file(__info.relative_path, 'md');
    });

    openTxtBtn.addEventListener('click', async function () {
        await open_file(__info.relative_path, 'txt');
    });

    async function open_file(path, type) {
        try {
            const response = await fetch('/api/open_file', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    dir_path: path,
                    file_type: type,
                })
            });
            const result = await response.json();
            alert(result.message);  // Whether succeess or not, alert response.
        } catch (error) {
            alert('错误:', error);
        }
    }
    closeResultBtn.addEventListener('click', closeResultModal);
}();

!function () {
    const doms = {
        form_container: document.querySelector('.form-container'),
    };
    function handleViewportResize() {
        const viewportWidth = window.innerWidth;
        if (viewportWidth < 700) {
            doms.form_container.style.transform = `scale(${viewportWidth / 700})`;
        } else {
            doms.form_container.style.transform = 'none';
        }
        doms.form_container.clientHeight;
    }
    handleViewportResize();
    setTimeout(handleViewportResize, 0);    // 必须执行两次，否则渲染会与预期不一致
    window.addEventListener('resize', handleViewportResize);
}();