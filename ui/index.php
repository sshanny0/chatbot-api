<!DOCTYPE html>
<html>

<head>
	<link rel="stylesheet" href="style.css">
</head>

<body>
	<div class="chat-bot">
		<div class="chat-content hidden" id="chatBox">
			<div class="chat-header">
				<div class="profile">
					<div class="profile-image">
						<img src="../img/icon-helpdesk.png" alt="icon-header">
					</div>
					<div>
						<p>UTI Chatbot</p>
					</div>
				</div>
				<div class="close-chat" id="closeChat">
					<svg viewBox="0 0 640 640" height="20px">
						<path fill="currentColor"
							d="M183.1 137.4C170.6 124.9 150.3 124.9 137.8 137.4C125.3 149.9 125.3 170.2 137.8 182.7L275.2 320L137.9 457.4C125.4 469.9 125.4 490.2 137.9 502.7C150.4 515.2 170.7 515.2 183.2 502.7L320.5 365.3L457.9 502.6C470.4 515.1 490.7 515.1 503.2 502.6C515.7 490.1 515.7 469.8 503.2 457.3L365.8 320L503.1 182.6C515.6 170.1 515.6 149.8 503.1 137.3C490.6 124.8 470.3 124.8 457.8 137.3L320.5 274.7L183.1 137.4z" />
					</svg>
				</div>
			</div>

			<div class="chat-body">
				<ul class="message">
					<li class="sender">
						<img src="../img/icon-helpdesk.png" alt="icon-message">
						<div class="message-content">
							<p>Halo, silahkan beritahu saya apabila Anda memiliki pertanyaan atau membutuhkan bantuan.</p>
						</div>
					</li>
										<li class="sender">
						<img src="../img/icon-helpdesk.png" alt="icon-message">
						<div class="message-content">
							<p>Pilih salah satu topik dibawah ini, atau ketik pertanyaan Anda!</p>
						</div>
					</li>
				</ul>

				                    <div class="quick-replies">
                        <button onclick="loadCategory('Helpdesk')">Getting Started</button>
                        <button onclick="loadCategory('Layanan Permintaan Link Zoom')">Zoom</button>
                        <button onclick="loadCategory('Layanan Aplikasi Master')">MASTER</button>
                        <button onclick="loadCategory('Layanan Aplikasi Kapten')">KAPTEN</button>
                        <button onclick="loadCategory('Layanan Aplikasi LMS')">LMS</button>
                        <button onclick="loadCategory('Layanan Aplikasi Drive')">Drive</button>
                        <button onclick="loadCategory('Layanan Email')">Email</button>
                        <button onclick="loadCategory('Layanan Koneksi Internet')">Network</button>
                        <button onclick="loadCategory('Layanan Anti Virus SentinelOne')">Antivirus</button>
                        <button onclick="loadCategory('Layanan Akun')">Single Sign-On (SSO)</button>
                    </div>
			</div>

			<div class="chat-footer">
				<input type="text" class="textInput" placeholder="Type your message">
				<button class="send-button">
					<svg viewBox="0 0 640 640" height="25px">
						<path fill="currentColor"
							d="M568.4 37.7C578.2 34.2 589 36.7 596.4 44C603.8 51.3 606.2 62.2 602.7 72L424.7 568.9C419.7 582.8 406.6 592 391.9 592C377.7 592 364.9 583.4 359.6 570.3L295.4 412.3C290.9 401.3 292.9 388.7 300.6 379.7L395.1 267.3C400.2 261.2 399.8 252.3 394.2 246.7C388.6 241.1 379.6 240.7 373.6 245.8L261.2 340.1C252.1 347.7 239.6 349.7 228.6 345.3L70.1 280.8C57 275.5 48.4 262.7 48.4 248.5C48.4 233.8 57.6 220.7 71.5 215.7L568.4 37.7z" />
					</svg>
				</button>
			</div>
		</div>

		<div class="chat-button" id="chatButton">
			<svg height="25px" viewBox="0 0 640 640">
				<path fill="currentColor"
					d="M115.9 448.9C83.3 408.6 64 358.4 64 304C64 171.5 178.6 64 320 64C461.4 64 576 171.5 576 304C576 436.5 461.4 544 320 544C283.5 544 248.8 536.8 217.4 524L101 573.9C97.3 575.5 93.5 576 89.5 576C75.4 576 64 564.6 64 550.5C64 546.2 65.1 542 67.1 538.3L115.9 448.9z" />
			</svg>
		</div>
	</div>

	<script src="script.js"></script>
</body>

</html>