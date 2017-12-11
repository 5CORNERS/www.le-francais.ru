var showMenu = !0, html5 = !1, subtractBy = 0, loaded = !1, gecko = !1, stopTime, player, speakingQuiztimeoutID = -1,
    timeID2 = -1;

function seekEvent() {
    player.play();
    timeID = setTimeout(stopNow, stopTime)
}

function setPlayerVariable() {
    var b = document.getElementById("launch_button");
    b.innerHTML = "Begin!";
    b.disabled = !1;
    (player = document.getElementsByTagName("audio")[0]) || (player = document.getElementsByTagName("video")[0]);
    navigator.userAgent.indexOf("AppleWebKit") !== -1 ? (slowSeek = !0, player.addEventListener("seeked", seekEvent, !1)) : navigator.userAgent.indexOf("Firefox") != -1 && (slowSeek = !0, player.addEventListener("seeked", seekEvent, !1), gecko = !0);
    player.play();
    player.readyState > 3 ? (timeID = setTimeout(stopNow, (times[0] -
        0.1) * 1E3 - player.currentTime), loaded = !0) : player.addEventListener("playing", function () {
        loaded || (stopAt(times[0] - 0.1), loaded = !0)
    }, !0)
}

function stopNow() {
    timeID = -1;
    player.pause();
    playing = !1;
    speakingQuiz && (speakingQuiztimeoutID = setTimeout(selectNextSpeakingQuizElement, 1500))
}

function stopSimple() {
    timeID = -1;
    player.pause();
    playing = !1
}

function setStopper(b) {
    stopTime = b
}

function stopNow2() {
    timeID2 = -1;
    player2.pause();
    playing = !1
}

function playAt(b) {
    player.currentTime = b;
    slowSeek || player.play()
}

function playAt2(b) {
    player2.currentTime = b
}

function play() {
    player.play()
}

function launch() {
    player.play();
    document.getElementById("launch_button").style.display = "none";
    document.getElementById("modalPage").style.display = "none"
};var originalArray, timeIndexes, currentIndex, missed = 0, timesIndex = -1, oldIndex = -2, id, timeID, slowSeek = !1,
    loadedVar = !1, delay = 1500, translationId = null, postPlayBeforeSelectSpeakingQuiz = !1, useAnimation = !0;

function stopNowRandom() {
    stopNow();
    quiz || (timeID = setTimeout(randomGenerator, delay * 1E3))
}

function stopAt(b) {
    timeID != -1 && window.clearTimeout(timeID);
    b *= 1E3;
    timeID = setTimeout(stopNow, b)
}

function getName(b) {
    return ie ? b.srcElement.name : b.target.getAttribute("name")
}

function clickOccurredNoTip() {
    clickOccurred(!0)
}

function clickOccurred(b, c) {
    var d = getId(b);
    if (quiz) guess(b, d); else if (showMenu) {
        var f = getTextToDisplay(d, !0, c),
            g = '<ul><li><a href="javascript:saveItem()">' + saveToAccount + "<br/> " + f + keyPressInfo + "</a></li></ul>",
            f = document.getElementById("context_menu");
        f.innerHTML = g;
        f.style.visibility = "visible";
        svg ? (d = document.getElementById(d), f.style.top = parseInt(tip.style.top, 10) + 280 + "px", f.style.left = tip.style.left) : (d = document.getElementById(d), d.getAttribute("name"), f.style.left = d.parentNode.offsetLeft + "px",
            f.style.top = d.parentNode.offsetTop + d.parentNode.offsetHeight + 50 + "px")
    }
}

var quiz = !1, menuId;

function getId(b) {
    var c;
    c = ie ? b.srcElement.id : b.target.id;
    c == "" && (c = ie && !html5 ? b.srcElement.parent.id : b.target.parentNode.id);
    if (c.indexOf("b") != -1) return c.substr(0, c.length - 1);
    return c
}

var messageDisplayed = !1, messageDiv, longMessageDisplayed;

function displayMessage(b, c) {
    messageDisplayed ? messageDiv = document.getElementById("message") : (messageDiv = document.createElement("div"), messageDiv.setAttribute("id", "message"), document.body.appendChild(messageDiv), messageDisplayed = !0);
    messageDiv.innerHTML = b;
    messageDiv.style.visibility = "visible";
    setTimeout(hideMessage, c)
}

function hideLongMessage() {
    document.getElementById("long_message").style.visibility = "hidden";
    document.onclick = clicked
}

function displayMessageUntilClick(b) {
    var c = document.getElementById("long_message");
    c == null && (c = document.createElement("div"), c.setAttribute("id", "long_message"), document.body.appendChild(c));
    c.innerHTML = b;
    c.style.visibility = "visible";
    window.setTimeout(function () {
        document.onclick = hideLongMessage
    }, 200)
}

function hideMessage() {
    messageDiv.style.visibility = "hidden"
}

var lockedID, locked = !1;

function unlock() {
    locked = !1;
    lockedID = -1
}

var hidePopupMode = !1;

function playSegment(b, c) {
    playSoundSegment(times[b], times[c])
}

var pressTimerId = -1;

function activateTimer(b) {
    deactivateTimer();
    pressTimerId = b ? setTimeout(clickOccurred, 2E3) : setTimeout(clickOccurredNoTip, 1E3)
}

function deactivateTimer() {
    pressTimerId != -1 && (window.clearTimeout(pressTimerId), pressTimerId = -1)
}

function getTargetElem(b) {
    var c;
    c = ie ? b.srcElement : b.target;
    c.id == "" && (c = ie && !html5 ? b.srcElement.parent : b.target.parentNode);
    return c
}

var oldClassName;

function selectElem(b) {
    if (selectedElem != null) if (b == selectedElem) return; else selectedElem.className = oldClassName, selectedElem = null;
    if (b.className.indexOf(" selected") == -1) oldClassName = b.className, b.className = oldClassName + " selected", selectedElem = b
}

var selectedElem;

function selectPlayAndShow(b) {
    var c = getTargetElem(b);
    selectElem(c);
    playAndShowId(b, c.id, !1)
}

function playAndShow(b) {
    id = getId(b);
    quiz ? guess(b, id) : (activateTimer(!0), playAndShowId(b, id, !0))
}

function playAndShowRow(b, c) {
    if (!quiz) {
        var d = getId(b);
        playAndShowId(b, d, c)
    }
}

function playAndShowParent(b, c) {
    if (!quiz) {
        var d = getParentId(b);
        playAndShowId(b, d, c)
    }
}

var timeIndex = -1;

function playAndShowId(b, c, d) {
    var f = parseInt(c), g = times[f];
    if (g != -1) {
        if (!locked || timeIndex !== f) timeIndex = f, locked = !0, lockedID = setTimeout(unlock, 300), f = times[timeIndex + 1], f == -1 && (f = getNextTime(timeIndex + 2)), playSoundSegment(g, f);
        hidePopupMode && (d = !1);
        if (d) d = document.getElementById("A" + c), g = d.innerHTML, f = d.getAttribute("grammar"), showTranslation && (d = document.getElementById("T" + c), d != null && (g = g + "<br /><em>(" + d.innerHTML + ")</em>")), showtip(b, g, f)
    }
}

function getNextTime(b) {
    for (var c = times[b]; c == -1 && b < times.length;) b++, c = times[b];
    return c
}

function computeAndGetTranslation(b) {
    b = Number(b);
    if (typeof translationMap !== "undefined") for (var c = translationMap.length, d = 0; d < c; d++) if (translationMap[d].id === b) return translationId = translationMap[d].tId, document.getElementById("T" + translationId);
    translationId = b + 1;
    return document.getElementById("T" + translationId)
}

function getTextToDisplay(b, c, d) {
    var d = d ? document.getElementById(b) : document.getElementById("A" + b), f = d.innerHTML;
    c && (d = document.getElementById("T" + b), d == null && (d = computeAndGetTranslation(b)), f = f + " <em>(" + d.innerHTML + ")</em>");
    return f
}

var showTranslation = !1;

function set() {
}

function hideDisabledDivs() {
    if (typeof disabledObjects != "undefined") for (var b = 0; b < disabledObjects.length; b++) document.getElementById(disabledObjects[b]).style.visibility = "hidden"
}

function setDivs() {
    var b = document.getElementsByTagName("div");
    if (b) {
        for (var c = [], d = 0, f = 0; f != b.length; f++) b[f].getAttribute("class") == "pictorial" && (c[d] = b[f], d++);
        processElements(c)
    }
}

function processElements(b) {
    for (var c = 0; c != b.length; c++) ie && !html5 ? (b[c].ontouchstart = function () {
        playAndShow(event)
    }, b[c].onclick = function () {
        clickOccurred(event, !1)
    }) : (b[c].ontouchstart = function (b) {
        playAndShow(b)
    }, b[c].addEventListener("touchstart", playAndShow, !1), b[c].addEventListener("touchend", popDown, !1)), b[c].onmouseout = popDown
}

function processElement(b) {
    ie && !html5 ? (b.ontouchstart = playAndShow, b.onclick = function () {
        clickOccurred(event, !1)
    }, b.ontouchend = function () {
        popDown()
    }) : (b.addEventListener("touchstart", playAndShow, !1), b.addEventListener("touchend", popDown, !1), b.addEventListener("click", doNothing, !1))
}

function doNothing() {
    event.cancelBubble = !0;
    event.stopPropagation && event.stopPropagation()
}

function audioEnd() {
    locked = !0;
    lockedID = setTimeout(unlock, 50);
    if (selectedElem != null) selectedElem.className = oldClassName, selectedElem = null
}

function processHoverElement(b) {
    ie && !html5 ? (b.ontouchstart = function () {
        playAndShow(e)
    }, b.ontouchend = audioEnd) : (b.addEventListener("touchstart", function (b) {
        selectPlayAndShow(b)
    }, !1), b.addEventListener("touchend", audioEnd), b.addEventListener("click", doNothing))
}

var selectedDiv, selectedTranslationDiv;

function selectorDiv(b) {
    var c = getId(b);
    selectedDiv = ie ? b.srcElement : b.target;
    c = selectedDiv.id;
    target.className = "audio selected";
    selectedTranslationDiv = document.getElementById("T" + c);
    for (b = parseInt(c); selectedTranslationDiv == null;) b--, selectedTranslationDiv = document.getElementById("T" + b);
    selectedTranslationDiv.className = "translation selected sub"
}

function selectorTranslation(b) {
    var b = getId(b), c = res = b.slice(1);
    selectedDiv = document.getElementById(c);
    selectedDiv.className = "audio selected";
    selectedTranslationDiv = document.getElementById(b);
    selectedTranslationDiv.className = "translation selected sub"
}

function selectorOff() {
    selectedDiv.className = "audio";
    selectedTranslationDiv.className = "translation sub"
}

function selectorOffTrans() {
    selectedDiv.className = "audio";
    selectedTranslationDiv.className = "translation sub"
}

var fieldset;

function selectGroup(b) {
    b = getId(b);
    fieldset = document.getElementById("f" + b);
    if (fieldset != null) fieldset.className = "selected"
}

function selectGroupOff() {
    if (fieldset != null) fieldset.className = "group"
}

function processByClass() {
    if (document.getElementsByClassName) {
        var b = document.getElementsByClassName("hover_title");
        b && b.length && b[0].addEventListener("touchstart", function () {
            playSound(-1)
        }, !1);
        var b = document.getElementsByClassName("audio");
        if (b) {
            for (var c = 0; c != b.length; c++) processHoverElement(b[c]);
            b = document.getElementsByClassName("grouplabel");
            for (c = 0; c != b.length; c++) b[c].addEventListener("touchstart", selectGroup, !1), b[c].addEventListener("touchend", selectGroupOff, !1);
            b = document.getElementsByClassName("sub");
            for (c = 0; c != b.length; c++) {
                var d = b[c];
                d.id.slice(0, 1) == "T" ? d.addEventListener("touchstart", selectorTranslation, !1) : d.addEventListener("touchstart",
                    selectorDiv, !1);
                d.addEventListener("touchend", selectorOff, !1)
            }
        }
    }
}

function ietruebody() {
    return document.compatMode && document.compatMode != "BackCompat" ? document.documentElement : document.body
}

function popDown() {
    deactivateTimer();
    if (tip != null) tip.style.visibility = "hidden", showing = !1
}

var keyPressInfo = "";

function keyListenerDown(b) {
    if (ie) b = window.event;
    b.keyCode == 27 && explore()
}

function keyListener(b) {
    if (ie) b = window.event;
    b.keyCode == 113 ? toggleQuiz() : b.keyCode == 104 ? toggleLabels() : b.keyCode == 32 ? speakingQuiz && (postPlayBeforeSelectSpeakingQuiz ? skipForwardSpeakingQuiz() : advanceSpeakingQuiz(), b.preventDefault()) : b.keyCode == 98 ? activeBeginnersMode() : b.keyCode == 105 ? activeIntermediateMode() : b.keyCode == 97 && activeAdvancedMode()
}

var currentDifficulty = 2, idAssociations = [], reverseIdAssociations = [];

function addAssoc(b, c) {
    idAssociations[b] = c;
    var d = reverseIdAssociations[c];
    d == null && (d = [], reverseIdAssociations[c] = d);
    d.push(b)
}

function hideDisabledObjects() {
    if (useSvg && typeof disabledObjects !== "undefined") for (var b = disabledObjects.length, c = 0; c < b; c++) SVGdoc.hideIdGroup(disabledObjects[c])
}

function activeBeginnersMode() {
    currentDifficulty == 1 ? subtractDifficulties(i) : currentDifficulty == 2 && (subtractDifficulties(i), subtractDifficulties(a));
    currentDifficulty = 0
}

var selectedCheckbox;

function activeIntermediateMode() {
    currentDifficulty == 0 ? addDifficulties(i) : currentDifficulty == 2 && subtractDifficulties(a);
    currentDifficulty = 1
}

function activeAdvancedMode() {
    currentDifficulty == 0 ? (addDifficulties(i), addDifficulties(a)) : currentDifficulty == 1 && addDifficulties(a);
    currentDifficulty = 2
}

function setCheckMark(b) {
    var c = document.getElementById("diff-indicator");
    if (selectedCheckbox != null) selectedCheckbox.innerHTML = "";
    b == 0 ? (selectedCheckbox = document.getElementById("beginner_c"), selectedCheckbox.innerHTML = "&#10003", c.className = "diff beginner") : b == 1 ? (selectedCheckbox = document.getElementById("intermediate_c"), selectedCheckbox.innerHTML = "&#10003", c.className = "diff intermediate") : (selectedCheckbox = document.getElementById("advanced_c"), selectedCheckbox.innerHTML = "&#10003", c.className = "diff advanced")
}

function isNotDisabled(b) {
    if (disabledObjects.indexOf(b) > -1) return !1;
    return !0
}

function addDifficulties(b) {
    var c = 0, d = b.length;
    if (useSvg) for (c = 0; c < d; c++) {
        var f = b[c];
        isNotDisabled(f) && SVGdoc.showIdGroup(f)
    }
    for (c = 0; c < d; c++) if (f = document.getElementById(b[c]), f != null) f.style.display = f.tagName === "TR" ? "table-row" : "block"
}

function subtractDifficulties(b) {
    var c = 0;
    if (useSvg) for (c = 0; c < b.length; c++) SVGdoc.hideIdGroup(b[c]);
    for (c = 0; c < b.length; c++) {
        var d = document.getElementById(b[c]);
        if (d) d.style.display = "none"
    }
}

var checkmark;

function toggleSpelling() {
    hidePopupMode = !hidePopupMode;
    return !0
}

function toggleAnimation() {
    useSvg && (useAnimation = !useAnimation, SVGdoc.useSelectionAnimation(useAnimation));
    return !0
}

function toggleOffensive(b, c) {
    b ? setCookie("prefs3", c + "1") : setCookie("prefs3", c + "0");
    return !1
}

var tip, ns6, ie, showing = !1, offsetfromcursorX = 2, offsetfromcursorY = 2;

function position(b, c, d, f) {
    var g = ns6 ? b.pageX : event.clientX + ietruebody().scrollLeft,
        h = ns6 ? b.pageY : event.clientY + ietruebody().scrollTop,
        j = ie && !window.opera ? ietruebody().clientWidth : window.innerWidth - 20,
        l = ie && !window.opera ? ietruebody().clientHeight : window.innerHeight - 20,
        l = ie && !window.opera ? l - event.clientY - f : l - b.clientY - f;
    c.style.left = (ie && !window.opera ? j - event.clientX - d : j - b.clientX - d) < c.offsetWidth ? g - c.offsetWidth + "px" : g < (d < 0 ? d * -1 : -1E3) ? "5px" : g + d + "px";
    c.style.top = l < c.offsetHeight ? h - c.offsetHeight - f +
        "px" : h + f + "px"
}

document.onmousemove = positiontip;
(function (b) {
    var c = navigator.userAgent.toLowerCase(), d = navigator.appName == "Microsoft Internet Explorer";
    html5 ? document.addEventListener("DOMContentLoaded", b, !1) : /webkit/.test(c) ? timeout = setTimeout(function () {
        document.readyState == "loaded" || document.readyState == "complete" ? b() : setTimeout(arguments.callee, 10)
    }, 10) : !d && /mozilla/.test(c) && !/(compatible)/.test(c) || /opera/.test(c) ? document.addEventListener("DOMContentLoaded", b, !1) : d ? (document.write("<script type='text/javascript' id='contentloadtag' defer='defer' src='javascript:void(0)'><\/script>"), document.getElementById("contentloadtag").onreadystatechange =
        function () {
            this.readyState == "complete" && b()
        }) : window.onload = b
})(init);

function svgclick(b) {
    if (!quiz) {
        var c = getId(b);
        menuId = idMappings[parseInt(c)]
    }
    clickOccurred(b, !1)
}

function processAreas() {
    var b = document.getElementsByTagName("area");
    if (b) for (var c = 0; c != b.length; c++) processElement(b[c])
}

function setLangAttribute() {
    if (typeof language !== "undefined" && typeof target !== "undefined" && language !== target) {
        for (var b = document.getElementsByClassName("w"), c = 0; c != b.length; c++) b[c].lang = language;
        b = document.getElementsByClassName("hover_title");
        for (c = 0; c != b.length; c++) b[c].lang = language;
        document.documentElement.lang = target
    }
}

function processDivs() {
    var b = document.getElementsByTagName("div");
    if (b) for (var c = 0; c != b.length; c++) {
        var d = b[c].getAttributeNode("class");
        d != null && d.value == "pictorial" && processElement(b[c])
    }
}

function processLinks() {
    var b = document.getElementsByTagName("a");
    if (b) for (var c = 0; c != b.length; c++) {
        var d = b[c].getAttributeNode("class");
        d != null && (d.value == "hover" ? processHoverElement(b[c]) : d.value == "pictorial" && processElement(b[c]))
    }
}

function initVariables() {
    ie = document.all;
    ns6 = document.getElementById && !document.all;
    typeof staticImage === "undefined" && (staticImage = !1);
    var b = localStorage.getItem("spelling");
    b !== null && b == "0" && (hidePopupMode = !0);
    b = localStorage.getItem("animation");
    b !== null && b == "0" && (useAnimation = !1)
}

var hasLinks = !0, hasDivs = !0;

function init() {
    document.onclick = clicked;
    initVariables();
    processAreas();
    hasDivs && (processDivs(), setLangAttribute());
    hasLinks && processLinks();
    processByClass();
    setPlayerVariable();
    document.onkeypress = keyListener;
    document.onkeydown = keyListenerDown;
    var b = document.getElementById("quiz");
    if (b != null) b.checked = !1;
    typeof useSvg === "undefined" && (useSvg = !1);
    useSvg || setDifficulty();
    createUserDiv();
    pointManager = new PointManager;
    // loadUserInfo()
}

function updateDifficultyDisplay() {
    var b = document.getElementById("difficultyDisplay");
    if (b != null) b.innerHTML = getDifficultyDisplayString()
}

function setDifficulty() {
    var b = localStorage.getItem("difficulty");
    typeof hasDifficulties !== "undefined" && hasDifficulties && (b != null ? b == 0 ? activeBeginnersMode() : b != 2 && activeIntermediateMode() : activeIntermediateMode(!1), updateDifficultyDisplay())
}

var svgOffsetTop, svgOffsetLeft, SVGdoc, svg = !1, showObjects = !0;

function svgInit(b) {
    SVGdoc = b;
    svg = document.getElementById("svg");
    svgOffsetTop = svg.offsetTop;
    svgOffsetLeft = svg.offsetLeft;
    svg.offsetParent != null && (svgOffsetTop = svg.offsetParent.offsetTop + svgOffsetTop, svgOffsetLeft = svg.offsetParent.offsetLeft + svgOffsetLeft);
    SVGdoc.showObjectsy(showObjects);
    mode == 2 ? (SVGdoc.initSpeakingQuiz(idAssociations, reverseIdAssociations), selectSpeakingQuizObject()) : mode == 1 && listen();
    currentDifficulty = 2;
    setDifficulty();
    hideDisabledObjects();
    useAnimation || SVGdoc.useSelectionAnimation(!1)
}

function setOldWidth() {
    if (svg) svg.style.position = "static", svg.style.border = "none", svg.width = "956px", svg.height = "auto"; else if (content != null) content.style.position = "static", content.removeEventListener("touchstart", toggleAdvanceSpeakingQuiz, !1);
    var b = document.getElementById("darkModalPage");
    document.body.removeChild(b);
    b = document.getElementById("x-out");
    document.body.removeChild(b)
}

function addDarkModel() {
    var b = document.createElement("div");
    b.id = "darkModalPage";
    b.addEventListener("click", exploreToggle);
    document.body.appendChild(b)
}

var content = null, firstTimeGuess = !1;

function setBestWidth(b) {
    var c = document.createElement("div");
    c.id = "x-out";
    c.style.top = "10px";
    c.style.right = "10px";
    c.addEventListener("click", exploreToggle);
    document.body.appendChild(c);
    addDarkModel();
    if (svg) c = svg.getBoundingClientRect().right, parseInt(c), c = document.documentElement.clientHeight - 55, b ? (svg.width = document.documentElement.clientWidth - 50 + "px", svg.height = c) : (b = svg.getBoundingClientRect(), b.width * (c / b.height) > document.documentElement.clientWidth ? svg.width = "100%" : (svg.width = "auto", svg.height =
        c)), svg.style.position = "absolute", svg.style.top = "45px", svg.style.left = 0, svg.style.right = 0, svg.style.margin = "auto", svg.style.backgroundColor = "white", firstTimeGuess = !0; else if (content = document.getElementById("content"), content != null) content.style.position = "absolute", content.style.height = document.documentElement.clientHeight - 50 + "px", content.style.width = "100%", content.style.overflow = "auto", content.style.top = "50px", content.style.left = 0, b && content.addEventListener("touchstart", toggleAdvanceSpeakingQuiz,
        !1)
}

var speakingSvg;

function randomGenerator() {
    setTimesIndex();
    var b = times[timesIndex];
    playAt(b);
    b = times[letterIndex + 1] - b;
    timeID != -1 && window.clearTimeout(timeID);
    timeID = setTimeout(stopNowRandom, b * 1E3)
}

function isActiveSVG(b) {
    if (hasDeactivatedQuizElements && deactivatedQuizElements.indexOf(b) != -1) return !1;
    if (currentDifficulty == 1) {
        if (a.indexOf(b) != -1) return !1
    } else if (currentDifficulty == 0) {
        if (a.indexOf(b) != -1) return !1;
        if (i.indexOf(b) != -1) return !1
    }
    return !0
}

function isActive(b) {
    if (hasDeactivatedQuizElements && deactivatedQuizElements.indexOf(b) != -1) return !1;
    if (hasDifficulties) if (currentDifficulty == 1) {
        if (a.indexOf(b) != -1) return !1
    } else if (currentDifficulty == 0) {
        if (a.indexOf(b) != -1) return !1;
        if (i.indexOf(b) != -1) return !1
    }
    return !0
}

function updateActiveQuizElements() {
    var b = [];
    for (p = 0; p < active.length; p++) if (active[p] == "true") {
        var c = document["group" + p];
        for (z = 0; z < c.length; z++) b.push(times[c[z]])
    }
    b.sort()
}

var activeQuizElements;

function createArrayIndexArray() {
    var b = times.length, c = [];
    if (svg) for (y = 0; y < b - 1; y++) {
        var d = times[y];
        d != -1 && isActiveSVG(y) && c.push(y)
    } else for (y = 0; y < b - 1; y++) d = times[y], d != -1 && isActive(y) && c.push(y);
    return c
}

var quizInited = !1, supportshtml5Audio, soundRoot = "/static/snd/";

function initQuizMode() {
    createAudioElement("quiz_audio");
    createAudioElement("tic")
}

function createAudioElement(b) {
    var c = document.createElement("audio");
    if (supportshtml5Audio = c.canPlayType) navigator.userAgent.indexOf("Firefox") == -1 && navigator.userAgent.indexOf("Chrome") == -1 ? c.setAttribute("src", soundRoot + b + ".m4a") : c.setAttribute("src", soundRoot + b + ".ogg"), c.load(), c.setAttribute("id", b), c.className = "pop_up", document.body.appendChild(c)
}

var ctrldown = !1, _quizModeOn = !1, hover_over_array, audioHoverOverArray;

function toggleQuizMode() {
    _quizModeOn ? deactivateQuizMode() : activateQuizMode()
}

function getWordNode(b) {
    if (b.className == "w") return b;
    for (var c = b.childNodes.length, d = 0; d != c; d++) {
        var f = getWordNode(b.childNodes[d]);
        if (f != null) return f
    }
    return null
}

var audioHoverOverArrayText;

function activateQuizMode() {
    _quizModeOn = !0;
    audioHoverOverArray = [];
    audioHoverOverArrayText = [];
    var b = document.getElementsByClassName("audio");
    if (b) for (var c = b.length, d = 0; d != c; d++) {
        var f = getWordNode(b[d]);
        if (f != null) audioHoverOverArrayText.push(f.innerHTML), audioHoverOverArray.push(f), f.innerHTML = "******"
    }
    hover_over_array = [];
    if (b = document.getElementsByTagName("a")) for (d = 0; d != b.length; d++) if (c = b[d], c.getAttribute("class") == "hover") hover_over_array.push(c.innerHTML), c.innerHTML = "******"
}

function deactivateQuizMode() {
    _quizModeOn = !1;
    var b = 0, c = document.getElementsByTagName("a");
    if (c) {
        for (var d = 0; d != c.length; d++) {
            var f = c[d];
            if (f.getAttribute("class") == "hover") f.innerHTML = hover_over_array[b], b++
        }
        b = audioHoverOverArray.length;
        for (d = 0; d != b; d++) audioHoverOverArray[d].innerHTML = audioHoverOverArrayText[d]
    }
}

var checkmarkNode, previouslyCheckedDiv, mode = 0, buttonControlId = "buttonControl";

function changeModeSelection() {
    var b = document.getElementById("explore");
    previouslyCheckedDiv == null && (previouslyCheckedDiv = b);
    var c = previouslyCheckedDiv.textContent;
    previouslyCheckedDiv.textContent = "";
    mode != 0 && (b = mode == 1 ? document.getElementById("listen") : document.getElementById("speak"));
    b.textContent = c;
    previouslyCheckedDiv = b
}

function createButton(b, c, d, f) {
    var g = document.createElement("button");
    f != null && g.setAttribute("style", f);
    g.setAttribute("readonly", "readonly");
    g.addEventListener("click", c, !1);
    g.innerHTML = b;
    d.appendChild(g);
    return g
}

function createButtonWithId(b, c, d, f, g) {
    b = createButton(b, d, f, g);
    b.id = c;
    return b
}

var quizModeHelpMsg = "Click on the image that corresponds best to the word you hear.";

function helpListen() {
    displayMessage(quizModeHelpMsg, 4E3)
}

function surrender() {
    alert("surrender")
}

function replay() {
    playLetter()
}

function skip() {
    alert("skip")
}

function showSpelling() {
    alert("showSpelling")
}

function removeButtonControlPanel() {
    var b = document.getElementById(buttonControlId);
    b.parentNode.removeChild(b)
}

function emptyButtonControlPanel() {
    var b = document.getElementById(buttonControlId);
    b.innerHTML = "";
    return b
}

function createButtonControlPanel() {
    var b = document.getElementById("nav");
    b == null && (b = document.getElementById("control"));
    var c = document.createElement("div");
    c.id = "buttonControl";
    b.parentNode.insertBefore(c, b.nextSibling);
    b = document.getElementById("svg");
    if (b != null) b.style.marginTop = "4px";
    return c
}

function listen() {
    if (mode != 1) {
        setBestWidth(!0);
        initListeningQuiz();
        var b;
        b = mode == 2 ? emptyButtonControlPanel() : createButtonControlPanel();
        mode = 1;
        createButton(generateButtonHtml("help.png", 32, 32), helpListen, b, "margin: 0 20px 0 0;-webkit-appearance: none;");
        createButton("show spelling", quizShowSpelling, b, "font-size: 125%;padding:10px 12px 11px; ");
        createButton(generateButtonHtml("skip_forward.png", 32, 32), quizSkip, b, "margin: 0 20px; padding: 6px 0 6px");
        createButton("replay " + generateButtonHtml("sound.png",
            13, 18), replay, b, "margin: 0 20px 0 0;font-size: 125%;padding:10px 12px 11px");
        pointManager.loadListeningPointsFromLocalStorage();
        activateQuiz();
        pointManager.startPointSavingTimer()
    }
}

function explore() {
    mode != 0 && (mode == 2 ? turnOffQuizMode() : quiz = !1, mode = 0, removeButtonControlPanel(), pointManager.cancelPointSavingTimer())
}

function helpSpeaking() {
    displayMessage(speakingQuizStartMsg, 4E3)
}

var paused = !1, speakingQuizElementSelected = !1;

function pauseSpeakingQuiz() {
    clearTimeout(speakingQuiztimeoutID);
    document.getElementById("pause").innerHTML = generateButtonHtml("9-av-play.png", 32, 32, null);
    paused = !0
}

function toggleAdvanceSpeakingQuiz() {
    postPlayBeforeSelectSpeakingQuiz || advanceSpeakingQuiz()
}

function advanceSpeakingQuiz() {
    pointManager.recordSpeakingCorrect(timesIndex);
    playLetter()
}

function skipForwardSpeakingQuiz() {
    speakingQuiztimeoutID != -1 && window.clearTimeout(speakingQuiztimeoutID);
    timeID != -1 && (window.clearTimeout(timeID), stopSimple());
    player.pause();
    playing = !1;
    selectNextSpeakingQuizElement()
}

var speakingQuizHistory;

function skipBackwardsSpeakingQuiz() {
}

function toggleSpeakingQuiz() {
    paused ? (clearTimeout(speakingQuiztimeoutID), paused = !1, postPlayBeforeSelectSpeakingQuiz ? selectNextSpeakingQuizElement() : (playLetter(), speakingQuizElementSelected = !1), document.getElementById("pause").innerHTML = generateButtonHtml("9-av-play.png", 32, 32)) : pauseSpeakingQuiz()
}

var advanceButton, skipForwardButton,
    speakingQuizHelp = '<div style="text-align:center;">(Click anywhere to close)</div><h3>Practice Speaking</h3><ol>  <li>Notice which object is selected. </li>  <li>Speak the word for it out loud.  </li>  <li>Click on the spacebar or the play button <button readonly="readonly" id="advance2"><img src="/vocabulary/images/9-av-play.png" align="absmiddle" width="32" height="32"></button> to hear the correct answer. </li></ol><p><strong>Microphone Mode (Beta)</strong> <br />If you use the google Chrome browser you can interact with the page using your voice. </p><ol>  <li>Click  on the microphone button.  </li>  <li>A panel at the top of the screen will request permission to use your microphone. Click on the \'Yes\' button.  </li>  <li>State the word for the selected object. You will then hear the correct answer. It\u2019s best to turn down the volume of your speakers or use headphones so the recorded voice isn\'t confused for your voice. </li></ol>';

function toggleHelpSpeaking() {
    displayMessageUntilClick(speakingQuizHelp)
}

function speak() {
    if (mode != 2) {
        timeID != -1 && (clearTimeout(timeID), stopSimple());
        setBestWidth(!0);
        var b;
        b = mode == 1 ? emptyButtonControlPanel() : createButtonControlPanel();
        svg && (staticImage ? SVGdoc.initSpeakingQuiz() : SVGdoc.initSpeakingQuiz(idAssociations, reverseIdAssociations));
        speakingQuizHistory = [];
        speakingQuizInitedFirstTime = !0;
        mode = 2;
        createButton(generateButtonHtml("help.png", 32, 32), toggleHelpSpeaking, b, "padding: 8px;margin-right: 20px;");
        advanceButton = createButtonWithId(generateButtonHtml("9-av-play.png",
            32, 32), "advance", advanceSpeakingQuiz, b, "-webkit-appearance: none;");
        advanceButton.className = "focus";
        skipForwardButton = createButtonWithId(generateButtonHtml("skip_forward.png", 32, 32), "skip_forward", skipForwardSpeakingQuiz, b, "padding: 8px;");
        pointManager.loadSpeakingPointsFromLocalStorage();
        startSpeakingQuiz();
        pointManager.startPointSavingTimer()
    }
}

function generateButtonHtml(b, c, d) {
    return '<img src="/static/images/' + b + '" align="absmiddle" width="' + c + '" height="' + d + '" />'
}

function activateQuiz() {
    speakingQuiz && turnOffQuizMode();
    startQuiz();
    quizInited || (quizInited = !0, setTimeout(initQuizMode, 1500))
}

function hideElement(b) {
    document.getElementById(b).style.visibility = "hidden"
}

function startQuiz() {
    speakingQuiz != null && clearQuizTimeout();
    quiz = !0;
    originalArray == null && (originalArray = createArrayIndexArray());
    timeIndexes = originalArray.slice();
    setTimeIndex();
    playSound(timesIndex)
}

function toggleSpeakingQuiz() {
    speakingQuiz ? turnOffQuizMode() : startSpeakingQuiz()
}

function turnOffQuizMode() {
    quiz = speakingQuiz = !1;
    if (svg) SVGdoc.deactivateSpeakingQuiz(), document.body.style.backgroundColor = "rgba(255,255,255,1)";
    speakingQuiztimeoutID != -1 && clearTimeout(speakingQuiztimeoutID);
    deselectSpeakingQuizElement()
}

function clearQuizTimeout() {
    timeID != -1 && (window.clearTimeout(timeID), stopNow())
}

var speakingQuiz = !1;

function startSpeakingQuiz() {
    quiz = speakingQuiz = !0;
    paused = !1;
    clearQuizTimeout();
    originalArray == null && (originalArray = createArrayIndexArray());
    timeIndexes = originalArray.slice();
    pointManager.removedAlreadyGuessedSpeaking(timeIndexes);
    selectNextSpeakingQuizElement()
}

function deselectSpeakingQuizElement() {
    if (hasSelectedElement) svg ? SVGdoc.hideGuess(timesIndex) : speakingQuizSelectedElement.className = previousClassName, hasSelectedElement = !1
}

function initSelectSpeakingQuizObject() {
    advanceButton.disabled = !1;
    advanceButton.className = "focus";
    skipForwardButton.className = "";
    postPlayBeforeSelectSpeakingQuiz = !1;
    speakingQuiztimeoutID = -1;
    deselectSpeakingQuizElement();
    speakingQuizInitedFirstTime ? speakingQuizInitedFirstTime = !1 : speakingQuizHistory.push(currentIndex)
}

function selectSpeakingQuizObject() {
    svg ? SVGdoc.guess(timesIndex) : (speakingQuizSelectedElement = document.getElementById(timesIndex), previousClassName = speakingQuizSelectedElement.className, speakingQuizSelectedElement.className += " quiz_selected");
    hasSelectedElement = !0
}

var speakingQuizSelectedElement, previousClassName, hasSelectedElement, microphoneListenMode = !1,
    speakingQuizInitedFirstTime;

function selectNextSpeakingQuizElement() {
    paused || (initSelectSpeakingQuizObject(), setTimeIndex(), removeTime(currentIndex), selectSpeakingQuizObject());
    recognition != null && (console.log("start"), recognition.start())
}

var speakingQuizHistoryIndex, skipBackwardSpeakingQuizButton;

function selectSpeakingQuizElementFromHistory() {
    if (!paused) {
        initSelectSpeakingQuizObject();
        if (speakingQuizHistoryIndex != -1) speakingQuizHistoryIndex = speakingQuizHistory.length;
        speakingQuizHistoryIndex--;
        if (speakingQuizHistoryIndex == 0) skipBackwardSpeakingQuizButton.disabled = !0;
        timesIndex = timeIndexes[speakingQuizHistory[speakingQuizHistoryIndex]];
        selectSpeakingQuizObject()
    }
}

function setTimeIndex() {
    var b = timeIndexes.length;
    if (b != 1 && b == 0) playAudio("tic"), mode === 1 ? pointManager.markListeningFinished(congratulationsMsg) : pointManager.markSpeakingFinished(congratulationsMsg), missed = 0, timeIndexes = originalArray.reverse(), b = timeIndexes.length;
    currentIndex = Math.floor(Math.random() * b);
    for (timesIndex = timeIndexes[currentIndex]; oldIndex == timesIndex & b > 1;) currentIndex = Math.floor(Math.random() * b), timesIndex = timeIndexes[currentIndex];
    oldIndex = timesIndex
}

function playLetter() {
    if (speakingQuiz) recognition != null && recognition.abort(), skipForwardButton.className = "focus", advanceButton.disabled = !0, advanceButton.className = "", postPlayBeforeSelectSpeakingQuiz = !0;
    playSound(timesIndex)
}

function removeTime(b) {
    var c = timeIndexes.slice(0, b), b = timeIndexes.slice(b + 1, timeIndexes.length);
    timeIndexes = c.concat(b)
}

function hideCheckmark() {
    checkmark.style.visibility = "hidden"
}

function hideWrong() {
    document.getElementById("wrong").style.visibility = "hidden"
}

function indicateCorrectAnswer(b) {
    checkmark.style.visibility = "visible";
    svg ? positionsvg(b, checkmark, -40, -40) : position(b, checkmark, -40, -40);
    setTimeout(hideCheckmark, 1E3)
}

function initListeningQuiz() {
    checkmark = document.getElementById("checkmark");
    checkmark == null && (checkmark = document.createElement("img"), checkmark.setAttribute("id", "checkmark"), checkmark.setAttribute("src", "/static/images/green_checkmark.png"), checkmark.setAttribute("style", "position:absolute;z-index:23"), document.body.appendChild(checkmark), hideCheckmark());
    var b = document.getElementById("wrong");
    b == null && (b = document.createElement("img"), b.setAttribute("id", "wrong"), b.setAttribute("src", "/static/images/wrong.png"),
        b.setAttribute("style", "position:absolute; z-index:23"), document.body.appendChild(b), hideWrong())
}

function indicateIncorrectAnswer(b) {
    wrong.style.visibility = "visible";
    svg ? positionsvg(b, wrong, -40, -40) : position(b, wrong, -40, -40);
    setTimeout(hideWrong, 1E3)
}

var notFirstTime = !1;

function playAudio(b) {
    if (supportshtml5Audio && (b = document.getElementById(b), b != null)) notFirstTime ? b.currentTime = 0 : notFirstTime = !0, b.play()
}

var points = 0, missedLastOne = !1;

function guess(b, c) {
    timesIndex == c ? (indicateCorrectAnswer(b), missedLastOne ? missedLastOne = !1 : (removeTime(currentIndex), pointManager.recordListeningCorrect(c)), setTimeIndex(), playSound(timesIndex)) : (missedLastOne = !0, playAudio("quiz_audio"), indicateIncorrectAnswer(b), missed++)
}

function playChain() {
}

function playSound(b) {
    timeID != -1 && (window.clearTimeout(timeID), timeID = -1, player.pause());
    var c;
    if (b == -1) {
        if (quiz) return;
        c = 0
    } else c = times[b];
    b = getValidEndTime(b) - c - subtractBy;
    slowSeek ? (setStopper(b * 1E3), playAt(c)) : (playAt(c), timeID = setTimeout(stopNow, b * 1E3))
}

function getValidEndTime(b) {
    b++;
    for (var c = times[b++]; c == -1 && b < times.length;) c = times[b], b++;
    return c
}

function playSoundSegment(b, c) {
    timeID != -1 && (window.clearTimeout(timeID), stopNow());
    var d = c - b - subtractBy;
    slowSeek ? (setStopper(d * 1E3), playAt(b)) : (playAt(b), timeID = setTimeout(stopNow, d * 1E3))
}

var showingAward = !1, onCloseCallback = null;

function addOnCloseCallback(b) {
    onCloseCallback = b
}

function clicked() {
    if (showingAward) {
        var b = document.getElementById("modalPage");
        document.body.removeChild(b);
        var b = document.getElementById("award"), c = document.getElementById("victory");
        c.pause();
        document.body.removeChild(b);
        document.body.removeChild(c);
        showingAward = !1;
        onCloseCallback != null && (onCloseCallback(), onCloseCallback = null)
    }
    b = document.getElementById("context_menu");
    if (b.style.visibility == "visible") return b.style.visibility = "hidden", !0;
    if (options != null && options.style.visibility == "visible") options.style.visibility =
        "hidden"
}

function saveItem() {
    storeWord();
    document.getElementById("context_menu").style.visibility = "hidden"
}

var req;

function storeWord() {
    var b = "/user/save_word.jsp?target=" + target + "&lang=" + language + "&id=" + menuId;
    if (translationId != null) {
        var c = document.getElementById(translationId).name;
        b += "&translationId=" + c;
        translationId = null
    }
    typeof XMLHttpRequest != "undefined" ? req = new XMLHttpRequest : window.ActiveXObject && (req = new ActiveXObject("Microsoft.XMLHTTP"));
    req.open("GET", b, !0);
    req.onreadystatechange = callback;
    req.send(null)
}

function quizSkip() {
    removeTime(currentIndex);
    setTimeIndex();
    playSound(timesIndex)
}

function quizShowSpelling() {
    var b = document.getElementById("A" + timesIndex).innerHTML;
    displayMessage(b, 2E3)
}

function display() {
}

function callback() {
    req.readyState == 4 && (req.status == 200 ? req.responseXML != null && req.responseXML.getElementsByTagName("message")[0].childNodes[0].value == "invalid" && alert("Please login. Click on 'My Account' to get a login prompt.") : alert("Please login. Click on 'My Account' to get a login prompt." + req.status))
}

var options;

function toggleDisplayOptions(b, c) {
    if (options != null && options.style.visibility == "visible" && (options.style.visibility = "hidden", options.id == c)) return;
    for (var d = document.getElementById(c + "Button"), f = d.offsetHeight, g = 0; d != null;) f += d.offsetTop, g += d.offsetLeft, d = d.offsetParent;
    options = document.getElementById(c);
    options.style.top = f + "px";
    options.style.left = g + "px";
    options.style.visibility = "visible";
    b.cancelBubble = !0;
    b.stopPropagation && b.stopPropagation()
}

var hasGroups = !1;

function remove(b) {
    if (useDiscreteElements) {
        var b = range(b), c = [];
        if (b.length == 0) for (var d = 1; d < range.length; d++) {
            b = range[d];
            for (z = 0; z < b.length; z++) value = currentArray[b[z]], c.push(value)
        } else for (d = start = 0; d < b.length; d++) {
            value = b[d];
            for (z = start; z < value; z++) toSave = currentArray[z], c.push(toSave);
            start = z + 1
        }
        currentArray = c
    }
}

function addRanges(b, c) {
    for (var d = b; d < c; d++) currentArray.push(d)
}

function add(b) {
    if (b == 0) {
        addRanges(0, range[b]);
        for (var c = 0; c < range[b]; c++) {
            var d = "letter" + c;
            document.getElementById(d).style.visibility = "visible"
        }
    } else {
        start = b == 0 ? 0 : range[b - 1];
        addRanges(start, range[b]);
        for (c = start; c < range[b]; c++) if (d = "letter" + c, !_slideshow) document.getElementById(d).style.visibility = "visible"
    }
}

active = [];

function changeGroup(b) {
    active[b.value] = b.checked ? !0 : !1;
    updateActiveQuizElements()
}

function setCookie(b, c, d) {
    var f = new Date;
    f.setDate(f.getDate() + d);
    c = escape(c) + (d == null ? "" : "; expires=" + f.toUTCString()) + "; path=/";
    document.cookie = b + "=" + c
}

function removeCookie(b) {
    document.cookie = b + "=; expires=Thu, 01-Jan-70 00:00:01 GMT; path=/"
}

function getCookie(b) {
    var c, d, f, g = document.cookie.split(";");
    for (c = 0; c < g.length; c++) if (d = g[c].substr(0, g[c].indexOf("=")), f = g[c].substr(g[c].indexOf("=") + 1), d = d.replace(/^\s+|\s+$/g, ""), d == b) return unescape(f)
}

var suggestionExpanded = !1;

function expandSuggestions() {
    var b = document.getElementById("suggest"), c = document.getElementById("suggestSymbol");
    suggestionExpanded ? (b.style.display = "none", suggestionExpanded = !1, c.innerHTML = "+") : (suggestionExpanded = !0, b.style.display = "block", c.innerHTML = "-")
}

function showtip(b, c, d) {
    tip = document.getElementById("popup");
    tip.innerHTML = c;
    tip.style.visibility = "visible";
    if (d != null) tip.style.backgroundColor = d == "m" ? "#DDDDFF" : d == "f" ? "#FFDDDD" : "#DDFFDD";
    showing = !0;
    var c = tip.offsetWidth, d = tip.offsetHeight, f = c / 2;
    svg ? positiontipsvg(b, tip, f, d, c) : positionsimple(b, tip, f, d)
}

function positiontipsvg(b, c, d, f, g) {
    if (showing) b = b.touches[0], c.style.top = b.pageY + svgOffsetTop - (f + 70) + "px", f = b.pageX + svgOffsetLeft - d, f < 0 ? f = 0 : b.pageX + d > document.documentElement.clientWidth && (f = document.documentElement.clientWidth - g + "px"), c.style.left = f + "px"
}

function positionsvg(b, c, d, f) {
    b = b.touches[0];
    c.style.top = b.pageY + d + "px";
    c.style.left = b.pageX + f + "px"
}

function positionsimple(b, c, d, f) {
    b = b.touches[0];
    c.style.top = b.pageY - (f + 60) + "px";
    f = b.pageX;
    b = f - d;
    if (b < 0) b = 0; else if (f + d > document.documentElement.clientWidth) {
        c.style.left = document.documentElement.clientWidth - (d + d) + "px";
        return
    }
    c.style.left = b + "px"
}

function positiontip(b) {
    showing && position(b, tip, 10, 20)
}

function speakToggle() {
    mode != 2 && speak()
}

function exploreToggle() {
    mode != 0 && (setOldWidth(), explore())
}

function listenToggle() {
    mode != 1 && (document.body.requestFullscreen && document.body.requestFullscreen(), listen())
}

function upgrade() {
    alert("Use of microphone only supported in webkit browsers (safari, chrome, chromium).")
}

function setUpMicrophoneLaunchIcon() {
    document.getElementById("mic").innerHTML = launchMicHTML
}

var launchMicHTML;

function toggleMicrophone() {
    microphoneListenMode ? (setUpMicrophoneLaunchIcon(), recognition.abort(), microphoneListenMode = !1) : launchMicrophone()
}

function speakToMicrophone() {
    playLetter()
}

var recognition;

function launchMicrophone() {
    "webkitSpeechRecognition" in window ? (microphoneListenMode = !0, document.getElementById("mic"), recognition = new webkitSpeechRecognition, Object.getOwnPropertyNames(recognition), recognition.continuous = !0, recognition.requiredConfidence = 0.1, recognition.interimResults = !1, recognition.lang = language, alert(recognition.lang), recognition.onstart = function () {
        var b = document.getElementById("mic");
        launchMicHTML = b.innerHTML;
        b.innerHTML = generateButtonHtml("mic_record.png", 50, 50, "margin-left: 20px;padding:2px 4px")
    },
        recognition.onresult = function (b) {
            for (var c = "", d = b.resultIndex; d < b.results.length; ++d) b.results[d].isFinal ? (final_transcript += b.results[d][0].transcript, postPlayBeforeSelectSpeakingQuiz || playLetter()) : c += b.results[d][0].transcript
        }, recognition.onerror = function (b) {
        displayMessage("An error occurred: " + b.error, 3E3);
        setUpMicrophoneLaunchIcon()
    }, recognition.onend = function () {
        setUpMicrophoneLaunchIcon();
        displayMessage("The microphone has been turned off. To continue click on the microphone button again.",
            3E3)
    }, final_transcript = "", recognition.start()) : upgrade()
}

var useLocalPoints = !0, pointsDiv;

function initPoints(b) {
    points = parseInt(b);
    pointsDiv = document.getElementById("points");
    pointsDiv.innerHTML = points
}

var userDiv, gameActivated = !1;

function createUserDiv() {
    if (localStorage.getItem("game") === "1" && language == "en") gameActivated = !0, userDiv = document.createElement("div"), userDiv.id = "user_div", userDiv.setAttribute("style", "position:absolute;right: 0px; top:0;padding:6px;text-align:right;"), pointsDiv = document.createElement("div"), pointsDiv.id = "points", pointsDiv.addEventListener("click", function () {
        window.location.href = "/user/points.jsp?lang=" + language
    }), document.body.appendChild(pointsDiv)
}

function userCallback() {
    if (req.readyState == 4 && req.status == 200) {
        var b = document.getElementsByTagName("body")[0],
            b = target != null && target !== "en" ? "?target=" + target : "";
        if (req.responseText != "{}") {
            var c = req.responseText, d, f = c.indexOf("^");
            f != -1 ? (d = c.substr(0, f), c.substr(f + 1, c.length - 1)) : d = c;
            c = document.createElement("div");
            c.id = "user2Button";
            c.className = "optionsButton";
            c.addEventListener("click", function () {
                toggleDisplayOptions(event, "user2", !0)
            }, !1);
            c.innerHTML = +d + '<img src="/static/images/down_arrow.png" width="10" height="6">';
            d = document.createElement("div");
            d.setAttribute("class", "options");
            d.id = "user2";
            c = document.createElement("div");
            c.setAttribute("onclick", "location.href='/user/account.jsp" + b + "'");
            c.setAttribute("class", "option link");
            c.innerHTML = savedWords;
            d.appendChild(c);
            c = document.createElement("div");
            c.innerHTML = logout;
            c.setAttribute("class", "option link");
            c.setAttribute("onclick", "location.href='/user/logout.jsp" + b + "'");
            d.appendChild(c);
            b = document.getElementsByTagName("body")[0];
            b.appendChild(d);
            registerVisit()
        }
    }
}

function loadUserInfo() {
    typeof XMLHttpRequest != "undefined" ? req = new XMLHttpRequest : window.ActiveXObject && (req = new ActiveXObject("Microsoft.XMLHTTP"));
    req.open("GET", "/user/getUserName.jsp", !0);
    req.onreadystatechange = userCallback;
    req.send(null)
}

var visitId, registeredVisit = !1, alreadyScored;

function visitRegistered() {
    if (req.readyState == 4 && req.status == 200) {
        var b = req.responseText, c = b.indexOf("-");
        c != -1 ? (visitId = b.substr(0, c), b = b.substr(c + 1, b.length - 1), alreadyScored = [], alreadyScored.push.apply(alreadyScored, b.split(",").map(Number))) : (visitId = b, alreadyScored = []);
        registeredVisit = !0
    }
}

function registerVisit() {
    if (typeof lgname != "undefined") {
        var b = "/user/visit.jsp?c=" + lgname + "&n=" + number + "&t=" + target + "&l=" + language;
        typeof XMLHttpRequest != "undefined" ? req = new XMLHttpRequest : window.ActiveXObject && (req = new ActiveXObject("Microsoft.XMLHTTP"));
        req.open("GET", b, !0);
        req.onreadystatechange = visitRegistered;
        req.send(null)
    }
}

function answerRegistered() {
}

var correctGuesses = [], correctSpeakingGuesses = [], pointManager = null;

function PointManager() {
    function b(b) {
        var c = localStorage.getItem("awards");
        c != null ? (awardArray = JSON.parse(c), typeof awardArray[language] == "undefined" && (awardArray[language] = [])) : (awardArray = {}, awardArray[language] = []);
        awardArray[language].push(b);
        b = JSON.stringify(awardArray);
        localStorage.setItem("awards", b)
    }

    function c() {
        var c = !1;
        typeof award != "undefined" && (d(lgname, award.desc), b(lgname), c = !0);
        if (typeof group !== "undefined") {
            for (var f = "g-" + group.name + "-" + language, g = localStorage.getItem(f), h = "", j = 0; j <
            group.total; j++) h += "1";
            if (g == null) {
                g = "";
                for (j = 0; j < group.total; j++) g += j == group.index ? "1" : "0"
            } else j = 0, j = g.substring(0, group.index) + 1, group.total > group.index + 1 && (j += g.substring(group.index + 1, g.length)), g = j;
            localStorage.setItem(f, g);
            g == h && (b(group.name), c ? addOnCloseCallback(function () {
                d(group.name, group.desc)
            }) : d(group.name, group.desc))
        }
    }

    function d(b, c) {
        if (gameActivated) {
            var d = document.createElement("div"), f = "<div>" + c + "</div>\t";
            d.id = "award";
            d.style.height = "300px";
            d.style.top = 0;
            d.style.backgroundColor =
                "#4b7aa4";
            d.style.display = "table-cell";
            d.style.verticalAlign = "middle";
            d.style.bottom = 0;
            var g = document.createElement("div"), h = document.createElement("div");
            h.style.height = "100%";
            h.style.verticalAlign = "middle";
            g.id = "modalPage";
            document.body.appendChild(g);
            showingAward = !0;
            d.style.left = 0;
            d.style.right = 0;
            d.style.width = "300px";
            d.style.margin = "auto";
            d.style.paddingTop = "10px";
            d.style.color = "white";
            d.style.padding = "14px;";
            d.style.position = "absolute";
            d.style.borderRadius = "140px";
            d.style.zIndex = 200;
            d.innerHTML =
                '<img src="/images/awards/' + (b + ".png") + '"  /><div style="width:200px; margin:auto">' + f + '</div><div style="margin-top:10px;"><img src="/static/images/x.png" width="40" height="40" /></div>';
            document.body.appendChild(d);
            createAudioElement("victory");
            playAudio("victory")
        }
    }

    function f() {
        var b = document.getElementById("listen"), c = b.innerHTML;
        b.style.paddingRight = "24px";
        b.innerHTML = c + x
    }

    function g() {
        var b = document.getElementById("speak");
        b.style.paddingRight = "28px";
        b.innerHTML += x
    }

    function h(b, c) {
        var d =
            localStorage.getItem(o);
        if (d != null) {
            var f = parseInt(d);
            f += b;
            localStorage.setItem(o, "" + f)
        } else localStorage.setItem(o, b);
        if (gameActivated) pointsDiv.innerHTML = f, b > 0 && (c += " You just earned " + b + " points.");
        displayMessage(c, 4E3)
    }

    var j = !1, l = !1, u = !1, s = null, o = "points-" + language, k = lgname + "-" + language, A = "lpoints-" + k,
        t = "spoints-" + k, v, q, m, w;
    this.resetPoints = function () {
        localStorage.clear()
    };
    this.processGroup = function () {
        c()
    };
    this.markListeningFinished = function (b) {
        r || (r = !0, h(q, b), q = 0, localStorage.setItem(t, 0), n ?
            (localStorage.setItem(k, "3"), c()) : localStorage.setItem(k, "1"), f())
    };
    var x = '<object data="/images/checkmark.svg" type="image/svg+xml" width="40px" height="40px" class="cm"> </object>';
    this.markSpeakingFinished = function (b) {
        n ? displayMessage("Starting over...", 2E3) : (n = !0, h(m, b), m = 0, localStorage.setItem(t, m), r ? (localStorage.setItem(k, "3"), c()) : localStorage.setItem(k, "2"), g())
    };
    this.removedAlreadyGuessedSpeaking = function (b) {
        var c = correctSpeakingGuesses.length;
        if (c > 0 && b.length !== c) for (var d = 0; d < c; d++) {
            var f =
                b.indexOf(correctSpeakingGuesses[d]);
            b.splice(f, 1)
        }
    };
    this.startPointSavingTimer = function () {
        s == null && (s = window.setInterval(this.savePointsLocally, 1E3))
    };
    this.cancelPointSavingTimer = function () {
        clearInterval(s);
        s = null;
        this.savePointsLocally()
    };
    this.savePointsLocally = function () {
        if (j) {
            j = !1;
            if (u) {
                localStorage.setItem(t, m);
                u = !1;
                var b = JSON.stringify(correctSpeakingGuesses);
                localStorage.setItem(v, b)
            }
            l && (localStorage.setItem(A, q), l = !1, b = JSON.stringify(correctGuesses), localStorage.setItem(w, b))
        }
    };
    var n, r;
    this.loadPointsFromLocalStorage =
        function () {
            var b = localStorage.getItem(o), c = localStorage.getItem(k);
            c != null && (c == 1 ? (f(), r = !0) : c == 2 ? (g(), n = !0) : c == 3 && (f(), g(), r = n = !0));
            c = localStorage.getItem(t);
            m = c != null ? new Number(c) : 0;
            c = localStorage.getItem(A);
            q = c != null ? new Number(c) : 0;
            b !== "undefined" && b !== "NaN" ? points = new Number(b) : (points = 0, localStorage.setItem(o, "0"));
            if (gameActivated) pointsDiv.innerHTML = points
        };
    this.loadListeningPointsFromLocalStorage = function () {
        w = k + "-clg";
        var b = localStorage.getItem(w);
        correctGuesses = b != null ? JSON.parse(b) : {}
    };
    this.loadSpeakingPointsFromLocalStorage = function () {
        v = k + "-csg";
        var b = localStorage.getItem(v);
        correctSpeakingGuesses = b != null ? JSON.parse(b) : []
    };
    this.recordSpeakingCorrect = function (b) {
        !n && correctSpeakingGuesses.indexOf(b) == -1 && (m += 1, j = !0, correctSpeakingGuesses.push(b), u = !0)
    };
    this.recordListeningCorrect = function (b) {
        correctGuesses[b] != 1 && (q += 2, j = !0, correctGuesses[b] = 1, l = !0)
    };
    this.loadPointsFromLocalStorage()
}

function toggleDisplayOptions(b, c, d) {
    if (options != null && options.style.visibility == "visible" && (options.style.visibility = "hidden", options.id == c)) return;
    for (var f = document.getElementById(c + "Button"), g = f.offsetHeight, h = 0; f != null;) g += f.offsetTop, h += f.offsetLeft, f = f.offsetParent;
    options = document.getElementById(c);
    options.style.top = g + "px";
    if (d) options.style.right = 0;
    options.style.visibility = "visible";
    b.cancelBubble = !0;
    b.stopPropagation && b.stopPropagation()
}

function getDifficultyDisplayString() {
    return currentDifficulty === 0 ? beginner : currentDifficulty === 1 ? intermediate : advanced
}

var hidePreferences = null;

function launchPreferences() {
    var b = null, c = document.createElement("div");
    c.id = "modalPage";
    document.body.appendChild(c);
    var d = document.createElement("div");
    d.id = "preferences";
    document.body.appendChild(d);
    createOptionRowFromStorage("spelling", d, spelling, toggleSpelling);
    createOptionRowFromStorage("animation", d, showAnimationText, toggleAnimation);
    b = document.createElement("div");
    if (typeof difficulty !== "undefined") b.innerHTML = difficulty;
    b.style.marginTop = "10px";
    b.style.borderBottom = "1px solid black";
    d.appendChild(b);
    createRadioRow("difficulty", "b", d, beginner);
    createRadioRow("difficulty", "i", d, intermediate);
    createRadioRow("difficulty", "a", d, advanced);
    createOptionRowFromCookie("offensive", d, showOffensiveContent, toggleOffensive);
    b = localStorage.getItem("difficulty");
    b = b === "0" ? document.getElementById("b") : b === "1" ? document.getElementById("i") : document.getElementById("a");
    b.checked = !0;
    var f = document.createElement("div");
    f.id = "x-out2";
    document.body.appendChild(f);
    hidePreferences = function () {
        document.body.removeChild(d);
        document.body.removeChild(f);
        document.body.removeChild(c);
        hidePreferences = null
    };
    c.addEventListener("click", hidePreferences, !1);
    f.addEventListener("click", hidePreferences, !1)
}

function createOptionRow(b, c, d, f) {
    var g = document.createElement("div");
    g.id = c + "row";
    b.appendChild(g);
    b = document.createElement("input");
    b.type = "checkbox";
    b.name = c;
    b.id = c;
    b.checked = f;
    b.style.pointerEvents = "none";
    g.appendChild(b);
    c = document.createElement("label");
    c.innerHTML = d;
    g.appendChild(c);
    return g
}

function createOptionRowFromStorage(b, c, d, f) {
    var g = localStorage.getItem(b);
    g == null || g == "1" ? (c = createOptionRow(c, b, d, !0), document.getElementById(b).checked = !0) : c = createOptionRow(c, b, d, !1);
    c.addEventListener("click", function () {
        var c = document.getElementById(b), d = f(!c.checked);
        c.checked ? (c.checked = !1, d && localStorage.setItem(b, "0")) : (c.checked = !0, d && localStorage.setItem(b, "1"))
    }, !1)
}

function createOptionRowFromCookie(b, c, d, f) {
    var g = !1, h = getCookie("prefs3");
    h != null && h.substring(2, 3) == "1" && (g = !0);
    c = createOptionRow(c, b, d, g);
    c.style.borderTop = "1px solid black";
    c.addEventListener("click", function () {
        var c = document.getElementById(b), d = h.substring(0, 2);
        f(!g, d);
        c.checked = c.checked ? !1 : !0
    }, !1)
}

function createRadioRow(b, c, d, f) {
    var g = null, h = document.createElement("div");
    h.id = c + "-row";
    d.appendChild(h);
    d = document.createElement("input");
    d.type = "radio";
    d.name = b;
    d.id = c;
    d.value = b;
    h.appendChild(d);
    b = document.createElement("label");
    b.innerHTML = f;
    h.appendChild(b);
    h.addEventListener("click", function () {
        h.id == "b-row" ? (g = document.getElementById("b"), localStorage.setItem("difficulty", "0"), activeBeginnersMode()) : h.id == "i-row" ? (g = document.getElementById("i"), localStorage.setItem("difficulty", "1"), activeIntermediateMode()) :
            h.id == "a-row" && (g = document.getElementById("a"), localStorage.setItem("difficulty", "2"), activeAdvancedMode());
        updateDifficultyDisplay();
        g.checked = !0
    }, !1)
};
