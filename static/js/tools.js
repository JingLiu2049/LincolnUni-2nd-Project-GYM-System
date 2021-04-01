function move(obj, attr, target, speed, callback) {
	clearInterval(obj.timer);

	var current = parseInt(getStyle(obj, attr));

	if(current > target) {
		speed = -speed;
	}

	obj.timer = setInterval(function() {

		var oldValue = parseInt(getStyle(obj, attr));

		var newValue = oldValue + speed;

		if((speed < 0 && newValue < target) || (speed > 0 && newValue > target)) {
			newValue = target;
		}

		obj.style[attr] = newValue + "px";

		if(newValue == target) {
			clearInterval(obj.timer);
			callback && callback();
		}

	}, 30);
}

function getStyle(obj, name) {

	if(window.getComputedStyle) {
		return getComputedStyle(obj, null)[name];
	} else {
		return obj.currentStyle[name];
	}

}
function addClass(obj, cn) {

	if(!hasClass(obj, cn)) {
		obj.className += " " + cn;
	}

}

function hasClass(obj, cn) {

	var reg = new RegExp("\\b" + cn + "\\b");

	return reg.test(obj.className);

}

function removeClass(obj, cn) {
	var reg = new RegExp("\\b" + cn + "\\b");

	obj.className = obj.className.replace(reg, "");

}

function toggleClass(obj, cn) {

	if(hasClass(obj, cn)) {
		removeClass(obj, cn);
	} else {
		addClass(obj, cn);
	}

}

function onchange_hidden(select,arr){

	select.onchange = function () {
		var value = select.value;
		for (var i = 0; i < arr.length; i++) {
			if (arr[i].textContent == value) {
				removeClass(arr[i].parentElement, "hidden")
			}
			else if (value == "all") {
				removeClass(arr[i].parentElement, "hidden")
			} else {
				addClass(arr[i].parentElement, "hidden")
			}
		}
	}

}

function insert_option(arr, selection) {
	var inner_list = [];
	for (var i = 0; i < arr.length; i++) {
		inner_list.push(arr[i].textContent)
	}
	var uni_arr = Array.from(new Set(inner_list))
	for (var i = 0; i < uni_arr.length; i++) {
		uni_arr[i] *= 1;
		var option = document.createElement("option");
		option.innerHTML = uni_arr[i];
		option.value = uni_arr[i];
		selection.appendChild(option);
	}
}
function test(text){
	console.log(text,typeof(text));
}