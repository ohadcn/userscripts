// ==UserScript==
// @id             HUJIINFOOCR
// @name           HUJI Personal Information form captcha idenifier
// @description    Auto fills the form to get login the personal information
// @version        1.1
// @namespace      ohadcn
// @author         Ohad Cohen & Shlomi Shasha
// @include        https://www.huji.ac.il/dataj/controller/stu/?
// @require        https://code.jquery.com/jquery-2.0.3.min.js
// @grant          GM_xmlhttpRequest
// @run-at         document-end
// ==/UserScript==

var ECRYPTED_SERVER = [104, 116, 116, 112, 58, 47, 47, 119, 119, 119, 46, 99, 115, 46, 104, 117, 106, 105, 46, 97, 99, 46, 105, 108, 47, 126, 111, 109, 101, 114, 115, 104, 101, 47, 99, 97, 112, 116, 99, 104, 97, 46, 112, 104, 112];
var server = "";
for (var i = 0; i < ECRYPTED_SERVER.length; i++)
{
	server += String.fromCharCode(ECRYPTED_SERVER[i]);
}

function getBase64Image(img) {
    var canvas = document.createElement("canvas");
    canvas.width = img.width;
    canvas.height = img.height;
    var ctx = canvas.getContext("2d");
    ctx.drawImage(img, 0, 0);
    var dataURL = canvas.toDataURL("image/png");
    return dataURL.replace(/^data:image\/(png|jpg);base64,/, "");
}

function showError(error) {
	$("#serverResponse").html(error).show();
}

unsafeWindow.retryCaptcha = function() {
	$(this).unbind("click");
	$(img).unbind("click").attr("src", IMAGE_PATH + "?d=" + new Date().getTime());
}

var img = $("img[alt=Captcha]").get(0);
var IMAGE_PATH = $(img).attr("src");

img.onload = function() {
	GM_xmlhttpRequest( {
		method: "POST",
        url: server,
		headers: {
			"Content-Type": "application/x-www-form-urlencoded"
		},
		data: "image=" + getBase64Image(img),
		onload: function(response) {
			var value = $.trim(response.responseText.replace(/\n/, ""));
			if (/^[0-9]{5,5}$/.test(value)) {
				$("#inputCaptcha").val(value);
				$("#serverResponse").hide();
			} else {
				if (/^[0-9\ ]+$/.test(value)) {
					$("#inputCaptcha").val(value);
					showError("שים לב: המספר פוענח חלקית");
				} else {
					$("#inputCaptcha").val("");
					showError("שגיאה בפענוח המספר");
				}
				$("#serverResponse").show();
			}
			$("#retry").click(unsafeWindow.retryCaptcha);
			$(img).click(unsafeWindow.retryCaptcha);
		},
		onerror: function() {
			$("#retry").click(unsafeWindow.retryCaptcha);
			$(img).click(unsafeWindow.retryCaptcha);
			showError("שגיאה כללית");
		},
		timeout: 7 * 1000
	});
}

var div = $(document.createElement("div"));
var retry = $(document.createElement("span"));
retry.css( {
	"direction": "rtl",
	"text-decoration": "underline",
	"cursor": "pointer"
	}).attr("id", "retry").click(unsafeWindow.retryCaptcha).html("נסה שוב");
var messageDiv = $(document.createElement("div")).attr("id", "serverResponse").css({"background-color":"yellow"}).hide();

div.append(retry).append(messageDiv);
$(img).click(unsafeWindow.retryCaptcha).css("cursor", "pointer").parent().append(div);

// Setting the tab index for the fields
$("#itz_id").attr("tabindex", 1).focus();
$("input[type=password]").attr("tabindex", 2);
$("a.jp-play").attr("tabindex", 100);
$("#inputCaptcha").attr("tabindex", 3);
retry.attr("tabindex", 4);
$("input[type=submit]").attr("tabindex", 5);
