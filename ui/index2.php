<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Chatbot Preview</title>

<style>
#chatbot-box {
    position: fixed;
    bottom: 90px;
    right: 20px;
    width: 360px;
    height: 520px;
    border: none;
    border-radius: 12px;
    overflow: hidden;
    z-index: 9999;
    display: none;
    background: #fff;
    box-shadow: 0 8px 25px rgba(0,0,0,0.25);
}

#chatbot-toggle {
    position: fixed;
    bottom: 25px;
    right: 25px;
    background: #2563eb;
    color: white;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    cursor: pointer;
    font-size: 26px;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

#chatbot-toggle:hover {
    background: #1d4ed8;
}
</style>
</head>

<body>


<div id="chatbot-box">
    <iframe 
        src="http://localhost:5500/ui/index.php"
        width="100%" 
        height="100%" 
        frameborder="0">
    </iframe>
</div>

<script>
document.getElementById('chatbot-toggle').onclick = function() {
    var box = document.getElementById('chatbot-box');
    box.style.display = (box.style.display === 'block') ? 'none' : 'block';
};
</script>

</body>
</html>
