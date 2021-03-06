var showMenu = !0, html5 = !0, subtractBy = .1, gecko = !1, player, stopTime, speakingQuiztimeoutID = -1;

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

function seekEvent() {
    player.play();
    timeID = setTimeout(stopNow, stopTime)
}

function stopPlayingTitle() {
    console.log("stopPlayingTitle");
    timeID = setTimeout(stopNow, 1E3 * (times[0] - .1) - player.currentTime);
    loadedVar = !0
}

var titleFinishedPlaying = !1;

function startPlaying() {
    player.addEventListener("play", function (b) {
        titleFinishedPlaying || (stopPlayingTitle(), titleFinishedPlaying = !0)
    }, !0);
    var b = player.play();
    void 0 !== b && b.then(function () {
    }).catch(function (b) {
        var c = document.createElement("button");
        c.style = "position: fixed;top: 50%;left: 50%;margin-top: -50px;margin-left: -100px;width: 250px;height: 100px;font-size: 200%;z-index: 501;";
        c.id = "launch";
        c.innerHTML = "Launch Audio";
        document.body.appendChild(c);
        c.focus();
        addDarkModel();
        c.addEventListener("click",
            function (b) {
                player.play();
                stopPlayingTitle();
                c.style.display = "none";
                document.getElementById("modalPage").style.display = "none";
                b.preventDefault();
                b.stopPropagation && b.stopPropagation()
            })
    })
}

function setPlayerVariable() {
    (player = document.getElementsByTagName("audio")[0]) || (player = document.getElementsByTagName("video")[0]);
    player && (player.addEventListener("canplaythrough", function () {
        startPlaying()
    }), -1 !== navigator.userAgent.indexOf("AppleWebKit") ? (slowSeek = !0, player.addEventListener("seeked", seekEvent, !1)) : -1 != navigator.userAgent.indexOf("Firefox") && (slowSeek = !0, player.addEventListener("seeked", seekEvent, !1), gecko = !0))
}

function setStopper(b) {
    stopTime = b
}

function stopNow2() {
    timeID = -1;
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
};var originalArray, timeIndexes, currentIndex, missed = 0, timesIndex = -1, oldIndex = -2, id, timeID, slowSeek = !1,
    loadedVar = !1, delay = 1500, translationId = null, postPlayBeforeSelectSpeakingQuiz = !1, useAnimation = !0;

function stopNowRandom() {
    stopNow();
    quiz || (timeID = setTimeout(randomGenerator, 1E3 * delay))
}

function stopAt(b) {
    -1 != timeID && window.clearTimeout(timeID);
    timeID = setTimeout(stopNow, 1E3 * b)
}

function getName(b) {
    return ie ? b.srcElement.name : b.target.getAttribute("name")
}

function clickOccurred(b, c) {
    var d = getId(b);
    if (quiz) guess(b, d); else if (showMenu) {
		playAndShow(b);
		c = getTextToDisplay(d, !0, c);
        c = '<ul><li>' + c + keyPressInfo + '</li></ul>';
        var e = document.getElementById("context_menu");
        e.innerHTML = c;
        e.style.visibility = "visible";
        svg ? positionsvg(b, e, 2, 2) : (menuId = getName(b), document.getElementById(d).getAttribute("name"), position(b, e, 2, 2));
        b.cancelBubble = !0;
        b.stopPropagation && b.stopPropagation()
    }
}

var quiz = !1, menuId;

function getId(b) {
    var c = ie ? b.srcElement.id : b.target.id;
    "" == c && (c = b.target.parentNode.id);
    return -1 != c.indexOf("b") ? c.substr(0, c.length - 1) : c
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
    null == c && (c = document.createElement("div"), c.setAttribute("id", "long_message"), document.body.appendChild(c));
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

function getTargetElem(b) {
    var c = ie ? b.srcElement : b.target;
    "" == c.id && (c = b.target.parentNode);
    return c
}

var oldClassName;

function selectElem(b) {
    if (null != selectedElem) {
        if (b == selectedElem) return;
        selectedElem.className = oldClassName;
        selectedElem = null
    }
    -1 == b.className.indexOf(" selected") && (oldClassName = b.className, b.className = oldClassName + " selected", selectedElem = b)
}

var selectedElem;

function selectPlayAndShow(b) {
    var c = getTargetElem(b);
    selectElem(c);
    var d = c.id;
    d || (d = c.parentElement.id);
    playAndShowId(b, d, !1)
}

function playAndShow(b) {
    if (!quiz) {
        var c = getId(b);
        playAndShowId(b, c, !0)
    }
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
    var e = parseInt(c), f = times[e];
    -1 != f && (locked && timeIndex === e || (timeIndex = e, locked = !0, lockedID = setTimeout(unlock, 300), e = times[timeIndex + 1], -1 == e && (e = getNextTime(timeIndex + 2)), playSoundSegment(f, e)), hidePopupMode && (d = !1), d && (d = document.getElementById("A" + c), f = d.innerHTML, e = d.getAttribute("grammar"), showTranslation && (d = document.getElementById("T" + c), null != d && (f = f + "<br /><em>(" + d.innerHTML + ")</em>")), showtip(b, f, e)))
}

function getNextTime(b) {
    for (var c = times[b]; -1 == c && b < times.length;) b++, c = times[b];
    return c
}

function computeAndGetTranslation(b) {
    b = Number(b);
    if ("undefined" !== typeof translationMap) for (var c = translationMap.length, d = 0; d < c; d++) if (translationMap[d].id === b) return translationId = translationMap[d].tId, document.getElementById("T" + translationId);
    translationId = b + 1;
    return document.getElementById("T" + translationId)
}

function getTextToDisplay(b, c, d) {
    d = d ? document.getElementById(b) : document.getElementById("A" + b);
    var e = d.innerHTML;
    c && (d = document.getElementById("T" + b), null == d && (d = computeAndGetTranslation(b)), e = e + " <em>(" + d.innerHTML + ")</em>");
    return e
}

var showTranslation = !1;

function set() {
}

function hideDisabledDivs() {
    if ("undefined" != typeof disabledObjects) for (var b = 0; b < disabledObjects.length; b++) document.getElementById(disabledObjects[b]).style.visibility = "hidden"
}

function setDivs() {
    var b = document.getElementsByTagName("div");
    if (b) {
        for (var c = [], d = 0, e = 0; e != b.length; e++) {
            var f = b[e];
            "pictorial" == f.getAttribute("class") && (c[d] = f, d++)
        }
        processElements(c);
        hideDisabledDivs()
    }
}

function processElements(b) {
    for (var c = 0; c != b.length; c++) b[c].onmouseover = function (b) {
        playAndShow(b)
    }, b[c].onclick = function (b) {
        clickOccurred(b, !1)
    }, b[c].onmouseout = popDown
}

function processElement(b) {
    ie && !html5 ? (b.onmouseover = playAndShow, b.onclick = function () {
        clickOccurred(event, !1)
    }) : (b.addEventListener("mouseover", playAndShow, !1), b.onclick = function (b) {
        clickOccurred(b, !1)
    }, b.onmousemove = positiontip);
    b.onmouseout = popDown
}

function audioEnd(b) {
    locked = !0;
    lockedID = setTimeout(unlock, 50);
    null != selectedElem && (selectedElem.className = oldClassName, selectedElem = null)
}

function processHoverElement(b) {
    ie && !html5 ? (b.onmouseover = function (b) {
        selectPlayAndShow(b)
    }, b.onclick = function () {
        clickOccurred(event, !0)
    }, b.onmouseout = popDown) : (b.addEventListener("mouseover", function (b) {
        selectPlayAndShow(b)
    }, !1), b.addEventListener("mouseout", audioEnd), b.addEventListener("click", function (b) {
        clickOccurred(b, !0)
    }, !1))
}

var selectedDiv, selectedTranslationDiv;

function selectorDiv(b) {
    getId(b);
    selectedDiv = ie ? b.srcElement : b.target;
    b = selectedDiv.id;
    target.className = "audio selected";
    selectedTranslationDiv = document.getElementById("T" + b);
    for (b = parseInt(b); null == selectedTranslationDiv;) b--, selectedTranslationDiv = document.getElementById("T" + b);
    selectedTranslationDiv.className = "translation selected sub"
}

function selectorTranslation(b) {
    b = getId(b);
    var c = res = b.slice(1);
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
    null != fieldset && (fieldset.className = "selected")
}

function selectGroupOff() {
    null != fieldset && (fieldset.className = "group")
}

function processByClass() {
    if (document.getElementsByClassName) {
        var b = document.getElementsByClassName("hover_title");
        b && b.length && b[0].addEventListener("touchstart", function () {
            playSound(-1)
        }, !1);
        var c = document.getElementsByClassName("audio");
        if (c) {
            for (b = 0; b != c.length; b++) processHoverElement(c[b]);
            c = document.getElementsByClassName("grouplabel");
            for (b = 0; b != c.length; b++) c[b].addEventListener("mouseover", selectGroup, !1), c[b].addEventListener("mouseout", selectGroupOff, !1);
            c = document.getElementsByClassName("sub");
            for (b = 0; b != c.length; b++) {
                var d = c[b];
                "T" == d.id.slice(0, 1) ? d.addEventListener("mouseover", selectorTranslation, !1) : d.addEventListener("mouseover", selectorDiv, !1);
                d.addEventListener("mouseout", selectorOff, !1)
            }
        }
    }
}

function ietruebody() {
    return document.compatMode && "BackCompat" != document.compatMode ? document.documentElement : document.body
}

function popDown() {
    null != tip && (tip.style.visibility = "hidden", showing = !1)
}

var keyPressInfo = "";

function keyListenerDown(b) {
    ie && (b = window.event);
    27 == b.keyCode && (null != hidePreferences ? hidePreferences() : exploreToggle())
}

function keyListener(b) {
    ie && (b = window.event);
    113 == b.keyCode ? toggleQuiz() : 104 == b.keyCode ? toggleLabels() : 32 == b.keyCode ? speakingQuiz && (postPlayBeforeSelectSpeakingQuiz ? skipForwardSpeakingQuiz() : advanceSpeakingQuiz(), b.preventDefault()) : 45 == b.keyCode ? (b = player.volume, 0 != b && (b = (b - .1).toFixed(1), player.volume = b, displayMessage(setVolumeTo + " " + 100 * b + "%", 3E3))) : 61 == b.keyCode ? (b = player.volume, 1 != b && (b = (b + .1).toFixed(1), player.volume = b, displayMessage(setVolumeTo + " " + 100 * b + "%", 3E3))) : 98 == b.keyCode ? activeBeginnersMode() :
        105 == b.keyCode ? activeIntermediateMode() : 97 == b.keyCode && activeAdvancedMode()
}

var currentDifficulty = 2, idAssociations = [], reverseIdAssociations = [];

function addAssoc(b, c) {
    idAssociations[b] = c;
    var d = reverseIdAssociations[c];
    null == d && (d = [], reverseIdAssociations[c] = d);
    d.push(b)
}

function hideDisabledObjects() {
    if (useSvg && "undefined" !== typeof disabledObjects) for (var b = disabledObjects.length, c = 0; c < b; c++) SVGdoc.hideIdGroup(disabledObjects[c]); else disabledObjects = []
}

function activeBeginnersMode() {
    1 == currentDifficulty ? subtractDifficulties(i) : 2 == currentDifficulty && (subtractDifficulties(i), subtractDifficulties(a));
    currentDifficulty = 0
}

var selectedCheckbox;

function activeIntermediateMode() {
    0 == currentDifficulty ? addDifficulties(i) : 2 == currentDifficulty && subtractDifficulties(a);
    currentDifficulty = 1
}

function activeAdvancedMode() {
    0 == currentDifficulty ? (addDifficulties(i), addDifficulties(a)) : 1 == currentDifficulty && addDifficulties(a);
    currentDifficulty = 2
}

function setCheckMark(b) {
    var c = document.getElementById("diff-indicator");
    null != selectedCheckbox && (selectedCheckbox.innerHTML = "");
    0 == b ? (selectedCheckbox = document.getElementById("beginner_c"), selectedCheckbox.innerHTML = "&#10003", c.className = "diff beginner") : 1 == b ? (selectedCheckbox = document.getElementById("intermediate_c"), selectedCheckbox.innerHTML = "&#10003", c.className = "diff intermediate") : (selectedCheckbox = document.getElementById("advanced_c"), selectedCheckbox.innerHTML = "&#10003", c.className = "diff advanced")
}

function isNotDisabled(b) {
    return -1 < disabledObjects.indexOf(b) ? !1 : !0
}

function addDifficulties(b) {
    var c, d = b.length;
    if (useSvg) for (c = 0; c < d; c++) {
        var e = b[c];
        isNotDisabled(e) && SVGdoc.showIdGroup(e)
    }
    for (c = 0; c < d; c++) e = document.getElementById(b[c]), null != e && (e.style.display = "TR" === e.tagName ? "table-row" : "block")
}

function subtractDifficulties(b) {
    var c;
    if (useSvg) for (c = 0; c < b.length; c++) SVGdoc.hideIdGroup(b[c]);
    for (c = 0; c < b.length; c++) {
        var d = document.getElementById(b[c]);
        d && (d.style.display = "none")
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

function position(b, c, d, e) {
    var f = ns6 ? b.pageX : event.clientX + ietruebody().scrollLeft,
        g = ns6 ? b.pageY : event.clientY + ietruebody().scrollTop,
        h = ie && !window.opera ? ietruebody().clientWidth : window.innerWidth - 20,
        l = ie && !window.opera ? ietruebody().clientHeight : window.innerHeight - 20;
    l = ie && !window.opera ? l - event.clientY - e : l - b.clientY - e;
    c.style.left = (ie && !window.opera ? h - event.clientX - d : h - b.clientX - d) < c.offsetWidth ? f - c.offsetWidth + "px" : f < (0 > d ? -1 * d : -1E3) ? "5px" : f + d + "px";
    c.style.top = l < c.offsetHeight ? g - c.offsetHeight - e +
        "px" : g + e + "px"
}

document.onmousemove = positiontip;
(function (b) {
    var c = navigator.userAgent.toLowerCase(), d = "Microsoft Internet Explorer" == navigator.appName;
    html5 ? document.addEventListener("DOMContentLoaded", b, !1) : !d && /mozilla/.test(c) && !/(compatible)/.test(c) || /opera/.test(c) ? document.addEventListener("DOMContentLoaded", b, !1) : d ? (document.write("<script type='text/javascript' id='contentloadtag' defer='defer' src='javascript:void(0)'>\x3c/script>"), document.getElementById("contentloadtag").onreadystatechange = function () {
        "complete" == this.readyState &&
        b()
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
    if ("undefined" !== typeof language && "undefined" !== typeof target && language !== target) {
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
        null != d && "pictorial" == d.value && processElement(b[c])
    }
}

function processLinks() {
    var b = document.getElementsByTagName("a");
    if (b) for (var c = 0; c != b.length; c++) {
        var d = b[c].getAttributeNode("class");
        null != d && ("hover" == d.value ? processHoverElement(b[c]) : "pictorial" == d.value && processElement(b[c]))
    }
}

function initVariables() {
    ie = document.all;
    ns6 = document.getElementById && !document.all;
    "undefined" === typeof staticImage && (staticImage = !1);
    var b = localStorage.getItem("spelling");
    null !== b && "0" == b && (hidePopupMode = !0);
    b = localStorage.getItem("animation");
    null !== b && "0" == b && (useAnimation = !1)
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
    window.addEventListener("resize", windowResize);
    document.onkeypress = keyListener;
    document.onkeydown = keyListenerDown;
    var b = document.getElementById("quiz");
    null != b && (b.checked = !1);
    "undefined" === typeof useSvg && (useSvg = !1);
    if (useSvg) {
        var c = null;
        setSvgSize();
        window.addEventListener("resize", function () {
            null != c && clearTimeout(c);
            c =
                setTimeout(function () {
                    setSvgSize()
                }, 500)
        })
    } else setDifficulty();
    createUserDiv();
    pointManager = new PointManager;
    // loadUserInfo()
}

function setSvgSize() {
    console.log("svg size");
    var b = document.getElementById("svg");
    if (b && "100%" !== b.width) {
        var c = document.documentElement.clientWidth, d = document.documentElement.clientHeight, e = b.scrollHeight,
            f = b.scrollWidth, g = f / e, h = b.getBoundingClientRect().top + window.scrollY + e;
        d > h ? (e += d - h - 27, d = e * g, d > c ? setToDefaultDimensions(b, f, g) : (b.height = e + "px", b.width = d + "px", b = document.getElementById("control"), null != b && (b.style.width = d + "px"))) : setToDefaultDimensions(b, f, g)
    }
}

function setToDefaultDimensions(b, c, d) {
    1020 > c && (b.width = "1020px", b.height = 1020 / d + "px")
}

function updateDifficultyDisplay() {
    var b = document.getElementById("difficultyDisplay");
    null != b && (b.innerHTML = getDifficultyDisplayString())
}

function setDifficulty() {
    var b = localStorage.getItem("difficulty");
    "undefined" !== typeof hasDifficulties && hasDifficulties && (null != b && (0 == b ? activeBeginnersMode() : 1 == b && activeIntermediateMode()), updateDifficultyDisplay())
}

var svgOffsetTop, svgOffsetLeft, SVGdoc, svg = !1, showObjects = !0;

function svgInit(b) {
    SVGdoc = b;
    svg = document.getElementById("svg");
    svgOffsetTop = svg.offsetTop;
    svgOffsetLeft = svg.offsetLeft;
    null != svg.offsetParent && (svgOffsetTop = svg.offsetParent.offsetTop + svgOffsetTop, svgOffsetLeft = svg.offsetParent.offsetLeft + svgOffsetLeft);
    SVGdoc.showObjectsy(showObjects);
    2 == mode ? (SVGdoc.initSpeakingQuiz(idAssociations, reverseIdAssociations), selectSpeakingQuizObject()) : 1 == mode && listen();
    currentDifficulty = 2;
    setDifficulty();
    hideDisabledObjects();
    useAnimation || SVGdoc.useSelectionAnimation(!1)
}

function setOldWidth() {
    svg ? (svg.style.position = "static", svg.style.border = "none", svg.width = "956px", svg.height = "auto") : null != content && (content.style.position = "static", content.removeEventListener("touchstart", toggleAdvanceSpeakingQuiz, !1));
    var b = document.getElementById("modalPage");
    document.body.removeChild(b);
    b = document.getElementById("x-out");
    document.body.removeChild(b)
}

function addDarkModel() {
    var b = document.createElement("div");
    b.id = "modalPage";
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
    svg ? (c = svg.getBoundingClientRect().right, parseInt(c), c = document.documentElement.clientHeight - 55, b ? (svg.width = document.documentElement.clientWidth - 50 + "px", svg.height = c) : (b = svg.getBoundingClientRect(), c / b.height * b.width > document.documentElement.clientWidth ? svg.width = "100%" : (svg.width = "auto", svg.height =
        c)), svg.style.position = "absolute", svg.style.top = "45px", svg.style.left = 0, svg.style.right = 0, svg.style.margin = "auto", svg.style.backgroundColor = "white", firstTimeGuess = !0) : (content = document.getElementById("content"), null != content && (content.style.position = "absolute", content.style.height = document.documentElement.clientHeight - 50 + "px", content.style.width = "100%", content.style.overflow = "auto", content.style.top = "50px", content.style.left = 0, b && content.addEventListener("touchstart", toggleAdvanceSpeakingQuiz, !1)))
}

var speakingSvg;

function randomGenerator() {
    setTimesIndex();
    var b = times[timesIndex];
    playAt(b);
    b = times[letterIndex + 1] - b;
    -1 != timeID && window.clearTimeout(timeID);
    timeID = setTimeout(stopNowRandom, 1E3 * b)
}

function isActiveSVG(b) {
    if (hasDeactivatedQuizElements && -1 != deactivatedQuizElements.indexOf(b)) return !1;
    if (1 == currentDifficulty) {
        if (-1 != a.indexOf(b)) return !1
    } else if (0 == currentDifficulty && (-1 != a.indexOf(b) || -1 != i.indexOf(b))) return !1;
    return !0
}

function isActive(b) {
    if (hasDeactivatedQuizElements && -1 != deactivatedQuizElements.indexOf(b)) return !1;
    if (hasDifficulties) if (1 == currentDifficulty) {
        if (-1 != a.indexOf(b)) return !1
    } else if (0 == currentDifficulty && (-1 != a.indexOf(b) || -1 != i.indexOf(b))) return !1;
    return !0
}

function updateActiveQuizElements() {
    var b = [];
    for (p = 0; p < active.length; p++) if ("true" == active[p]) {
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
        -1 != d && isActiveSVG(y) && c.push(y)
    } else for (y = 0; y < b - 1; y++) d = times[y], -1 != d && isActive(y) && c.push(y);
    return c
}

var quizInited = !1, supportshtml5Audio, soundRoot = "/static/snd/";

function initQuizMode() {
    createAudioElement("quiz_audio");
    createAudioElement("tic")
}

function createAudioElement(b) {
    var c = document.createElement("audio");
    if (supportshtml5Audio = c.canPlayType) -1 == navigator.userAgent.indexOf("Firefox") && -1 == navigator.userAgent.indexOf("Chrome") ? c.setAttribute("src", soundRoot + b + ".m4a") : c.setAttribute("src", soundRoot + b + ".ogg"), c.load(), c.setAttribute("id", b), c.className = "pop_up", document.body.appendChild(c)
}

var ctrldown = !1, _quizModeOn = !1, hover_over_array, audioHoverOverArray;

function toggleQuizMode() {
    _quizModeOn ? deactivateQuizMode() : activateQuizMode()
}

function getWordNode(b) {
    if ("w" == b.className) return b;
    for (var c = b.childNodes.length, d = 0; d != c; d++) {
        var e = getWordNode(b.childNodes[d]);
        if (null != e) return e
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
        var e = getWordNode(b[d]);
        null != e && (audioHoverOverArrayText.push(e.innerHTML), audioHoverOverArray.push(e), e.innerHTML = "******")
    }
    hover_over_array = [];
    if (b = document.getElementsByTagName("a")) for (d = 0; d != b.length; d++) c = b[d], "hover" == c.getAttribute("class") && (hover_over_array.push(c.innerHTML), c.innerHTML = "******")
}

function deactivateQuizMode() {
    _quizModeOn = !1;
    var b = 0, c = document.getElementsByTagName("a");
    if (c) {
        for (var d = 0; d != c.length; d++) {
            var e = c[d];
            "hover" == e.getAttribute("class") && (e.innerHTML = hover_over_array[b], b++)
        }
        b = audioHoverOverArray.length;
        for (d = 0; d != b; d++) audioHoverOverArray[d].innerHTML = audioHoverOverArrayText[d]
    }
}

var checkmarkNode, previouslyCheckedDiv, mode = 0, buttonControlId = "buttonControl";

function changeModeSelection() {
    var b = document.getElementById("explore");
    null == previouslyCheckedDiv && (previouslyCheckedDiv = b);
    var c = previouslyCheckedDiv.textContent;
    previouslyCheckedDiv.textContent = "";
    0 != mode && (b = 1 == mode ? document.getElementById("listen") : document.getElementById("speak"));
    b.textContent = c;
    previouslyCheckedDiv = b
}

function createButton(b, c, d, e) {
    var f = document.createElement("button");
    null != e && f.setAttribute("style", e);
    f.setAttribute("readonly", "readonly");
    f.addEventListener("click", c, !1);
    f.innerHTML = b;
    d.appendChild(f);
    return f
}

function createButtonWithId(b, c, d, e, f) {
    b = createButton(b, d, e, f);
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
    null == b && (b = document.getElementById("control"));
    var c = document.createElement("div");
    c.id = "buttonControl";
    b.parentNode.insertBefore(c, b.nextSibling);
    b = document.getElementById("svg");
    null != b && (b.style.marginTop = "4px");
    return c
}

function listen() {
    if (1 != mode) {
        setBestWidth(!0);
        initListeningQuiz();
        var b = 2 == mode ? emptyButtonControlPanel() : createButtonControlPanel();
        mode = 1;
        createButton(generateButtonHtml("help.png", 32, 32), helpListen, b, "margin: 0 20px 0 0;padding: 6px;");
        createButton("show spelling", quizShowSpelling, b, "font-size: 125%;padding:10px 12px 11px; ");
        createButton(generateButtonHtml("skip_forward.png", 32, 32), quizSkip, b, "margin: 0 20px; padding: 6px 0 6px");
        createButton("replay " + generateButtonHtml("sound.png", 13, 18), replay,
            b, "margin: 0 20px 0 0;font-size: 125%;padding:10px 12px 11px");
        pointManager.loadListeningPointsFromLocalStorage();
        activateQuiz();
        pointManager.startPointSavingTimer()
    }
}

function explore() {
    0 != mode && (2 == mode ? turnOffQuizMode() : quiz = !1, mode = 0, removeButtonControlPanel(), pointManager.cancelPointSavingTimer())
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
    -1 != speakingQuiztimeoutID && window.clearTimeout(speakingQuiztimeoutID);
    -1 != timeID && (window.clearTimeout(timeID), stopSimple());
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

var advanceButton, skipForwardButton;

function toggleHelpSpeaking() {
    displayMessageUntilClick(speakingQuizHelp)
}

function speak() {
    if (2 != mode) {
        -1 != timeID && (clearTimeout(timeID), stopSimple());
        setBestWidth(!0);
        var b = 1 == mode ? emptyButtonControlPanel() : createButtonControlPanel();
        svg && (staticImage ? SVGdoc.initSpeakingQuiz() : SVGdoc.initSpeakingQuiz(idAssociations, reverseIdAssociations));
        speakingQuizHistory = [];
        speakingQuizInitedFirstTime = !0;
        mode = 2;
        createButton(generateButtonHtml("help.png", 32, 32), helpSpeaking, b, "padding: 8px;margin-right: 20px;");
        advanceButton = createButtonWithId(generateButtonHtml("9-av-play.png", 32,
            32), "advance", advanceSpeakingQuiz, b, null);
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
    null != speakingQuiz && clearQuizTimeout();
    quiz = !0;
    null == originalArray && (originalArray = createArrayIndexArray());
    timeIndexes = originalArray.slice();
    setTimeIndex();
    playSound(timesIndex)
}

function toggleSpeakingQuiz() {
    speakingQuiz ? turnOffQuizMode() : startSpeakingQuiz()
}

function turnOffQuizMode() {
    quiz = speakingQuiz = !1;
    svg && (SVGdoc.deactivateSpeakingQuiz(), document.body.style.backgroundColor = "rgba(255,255,255,1)");
    -1 != speakingQuiztimeoutID && clearTimeout(speakingQuiztimeoutID);
    deselectSpeakingQuizElement()
}

function clearQuizTimeout() {
    -1 != timeID && (window.clearTimeout(timeID), stopNow())
}

function windowResize() {
    svgOffsetTop = svg.offsetTop;
    svgOffsetLeft = svg.offsetLeft;
    null != svg.offsetParent && (svgOffsetTop = svg.offsetParent.offsetTop + svgOffsetTop, svgOffsetLeft = svg.offsetParent.offsetLeft + svgOffsetLeft)
}

var speakingQuiz = !1;

function startSpeakingQuiz() {
    quiz = speakingQuiz = !0;
    paused = !1;
    clearQuizTimeout();
    null == originalArray && (originalArray = createArrayIndexArray());
    timeIndexes = originalArray.slice();
    pointManager.removedAlreadyGuessedSpeaking(timeIndexes);
    selectNextSpeakingQuizElement()
}

function deselectSpeakingQuizElement() {
    hasSelectedElement && (svg ? SVGdoc.hideGuess(timesIndex) : speakingQuizSelectedElement.className = previousClassName, hasSelectedElement = !1)
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
    null != recognition && (console.log("start"), recognition.start())
}

var speakingQuizHistoryIndex, skipBackwardSpeakingQuizButton;

function selectSpeakingQuizElementFromHistory() {
    paused || (initSelectSpeakingQuizObject(), -1 != speakingQuizHistoryIndex && (speakingQuizHistoryIndex = speakingQuizHistory.length), speakingQuizHistoryIndex--, 0 == speakingQuizHistoryIndex && (skipBackwardSpeakingQuizButton.disabled = !0), timesIndex = timeIndexes[speakingQuizHistory[speakingQuizHistoryIndex]], selectSpeakingQuizObject())
}

function setTimeIndex() {
    var b = timeIndexes.length;
    1 != b && 0 == b && (playAudio("tic"), 1 === mode ? pointManager.markListeningFinished(congratulationsMsg) : pointManager.markSpeakingFinished(congratulationsMsg), missed = 0, timeIndexes = originalArray.reverse(), b = timeIndexes.length);
    currentIndex = Math.floor(Math.random() * b);
    for (timesIndex = timeIndexes[currentIndex]; oldIndex == timesIndex & 1 < b;) currentIndex = Math.floor(Math.random() * b), timesIndex = timeIndexes[currentIndex];
    oldIndex = timesIndex
}

function playLetter() {
    speakingQuiz && (null != recognition && recognition.abort(), skipForwardButton.className = "focus", advanceButton.disabled = !0, advanceButton.className = "", postPlayBeforeSelectSpeakingQuiz = !0);
    playSound(timesIndex)
}

function removeTime(b) {
    var c = timeIndexes.slice(0, b);
    b = timeIndexes.slice(b + 1, timeIndexes.length);
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
    null == checkmark && (checkmark = document.createElement("img"), checkmark.setAttribute("id", "checkmark"), checkmark.setAttribute("src", "/static/images/green_checkmark.png"), checkmark.setAttribute("style", "position:absolute;z-index:23"), document.body.appendChild(checkmark), hideCheckmark());
    var b = document.getElementById("wrong");
    null == b && (b = document.createElement("img"), b.setAttribute("id", "wrong"), b.setAttribute("src", "/static/images/wrong.png"),
        b.setAttribute("style", "position:absolute; z-index:23"), document.body.appendChild(b), hideWrong())
}

function indicateIncorrectAnswer(b) {
    wrong.style.visibility = "visible";
    svg ? positionsvg(b, wrong, -40, -40) : position(b, wrong, -40, -40);
    setTimeout(hideWrong, 1E3)
}

function playAudio(b) {
    b = document.getElementById(b);
    null != b && (b.currentTime = 0, b.play())
}

var points = 0, missedLastOne = !1;

function guess(b, c) {
    timesIndex == c ? (indicateCorrectAnswer(b), missedLastOne ? missedLastOne = !1 : (removeTime(currentIndex), pointManager.recordListeningCorrect(c)), setTimeIndex(), playSound(timesIndex)) : (missedLastOne = !0, playAudio("quiz_audio"), indicateIncorrectAnswer(b), missed++)
}

function playChain() {
}

function playSound(b) {
    -1 != timeID && (window.clearTimeout(timeID), timeID = -1, player.pause());
    if (-1 == b) {
        if (quiz) return;
        var c = 0
    } else c = times[b];
    b = getValidEndTime(b) - c - subtractBy;
    slowSeek ? (setStopper(1E3 * b), playAt(c)) : (playAt(c), timeID = setTimeout(stopNow, 1E3 * b))
}

function getValidEndTime(b) {
    b++;
    for (var c = times[b++]; -1 == c && b < times.length;) c = times[b], b++;
    return c
}

function playSoundSegment(b, c) {
    -1 != timeID && (window.clearTimeout(timeID), stopNow());
    c = c - b - subtractBy;
    slowSeek ? (setStopper(1E3 * c), playAt(b)) : (playAt(b), timeID = setTimeout(stopNow, 1E3 * c))
}

var showingAward = !1, onCloseCallback = null;

function addOnCloseCallback(b) {
    onCloseCallback = b
}

function clicked() {
    if (showingAward) {
        var b = document.getElementById("modalPage");
        document.body.removeChild(b);
        b = document.getElementById("award");
        var c = document.getElementById("victory");
        c.pause();
        document.body.removeChild(b);
        document.body.removeChild(c);
        showingAward = !1;
        null != onCloseCallback && (onCloseCallback(), onCloseCallback = null)
    }
    b = document.getElementById("context_menu");
    if ("visible" == b.style.visibility) return b.style.visibility = "hidden", !0;
    null != options && "visible" == options.style.visibility && (options.style.visibility =
        "hidden")
}

function saveItem() {
    storeWord();
    document.getElementById("context_menu").style.visibility = "hidden"
}

var req;

function storeWord() {
    var b = "/user/save_word.jsp?target=" + target + "&lang=" + language + "&id=" + menuId;
    if (null != translationId) {
        var c = document.getElementById(translationId).name;
        b += "&translationId=" + c;
        translationId = null
    }
    "undefined" != typeof XMLHttpRequest ? req = new XMLHttpRequest : window.ActiveXObject && (req = new ActiveXObject("Microsoft.XMLHTTP"));
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
    4 == req.readyState && (200 == req.status ? null != req.responseXML && "invalid" == req.responseXML.getElementsByTagName("message")[0].childNodes[0].value && alert("Please login. Click on 'My Account' to get a login prompt.") : alert("Please login. Click on 'My Account' to get a login prompt." + req.status))
}

var options;

function toggleDisplayOptions(b, c) {
    if (null != options && "visible" == options.style.visibility && (options.style.visibility = "hidden", options.id == c)) return;
    for (var d = document.getElementById(c + "Button"), e = d.offsetHeight, f = 0; null != d;) e += d.offsetTop, f += d.offsetLeft, d = d.offsetParent;
    options = document.getElementById(c);
    options.style.top = e + "px";
    options.style.left = f + "px";
    options.style.visibility = "visible";
    b.cancelBubble = !0;
    b.stopPropagation && b.stopPropagation()
}

var hasGroups = !1;

function remove(b) {
    if (useDiscreteElements) {
        b = range(b);
        var c = [];
        if (0 == b.length) for (var d = 1; d < range.length; d++) for (b = range[d], z = 0; z < b.length; z++) value = currentArray[b[z]], c.push(value); else for (d = start = 0; d < b.length; d++) {
            value = b[d];
            for (z = start; z < value; z++) toSave = currentArray[z], c.push(toSave);
            start = z + 1
        }
        currentArray = c
    }
}

function addRanges(b, c) {
    for (; b < c; b++) currentArray.push(b)
}

function add(b) {
    if (0 == b) {
        addRanges(0, range[b]);
        for (var c = 0; c < range[b]; c++) {
            var d = "letter" + c;
            document.getElementById(d).style.visibility = "visible"
        }
    } else for (start = 0 == b ? 0 : range[b - 1], addRanges(start, range[b]), c = start; c < range[b]; c++) d = "letter" + c, _slideshow || (document.getElementById(d).style.visibility = "visible")
}

active = [];

function changeGroup(b) {
    active[b.value] = b.checked ? !0 : !1;
    updateActiveQuizElements()
}

function setCookie(b, c, d) {
    var e = new Date;
    e.setDate(e.getDate() + d);
    c = escape(c) + (null == d ? "" : "; expires=" + e.toUTCString()) + "; path=/";
    document.cookie = b + "=" + c
}

function removeCookie(b) {
    document.cookie = b + "=; expires=Thu, 01-Jan-70 00:00:01 GMT; path=/"
}

function getCookie(b) {
    var c, d = document.cookie.split(";");
    for (c = 0; c < d.length; c++) {
        var e = d[c].substr(0, d[c].indexOf("="));
        var f = d[c].substr(d[c].indexOf("=") + 1);
        e = e.replace(/^\s+|\s+$/g, "");
        if (e == b) return unescape(f)
    }
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
    null != d && (tip.style.backgroundColor = "m" == d ? "#DDDDFF" : "f" == d ? "#FFDDDD" : "#DDFFDD");
    showing = !0;
    svg ? positiontipsvg(b) : position(b, tip, 10, 20)
}

function positiontipsvg(b) {
    showing && (tip.style.top = b.clientY + svgOffsetTop + 10 + "px", tip.style.left = b.clientX + svgOffsetLeft + 20 + "px")
}

function positionsvg(b, c, d, e) {
    c.style.top = b.clientY + svgOffsetTop + d + "px";
    c.style.left = b.clientX + svgOffsetLeft + e + "px"
}

function positiontip(b) {
    showing && position(b, tip, 10, 20)
}

function speakToggle() {
    2 != mode && speak()
}

function exploreToggle() {
    0 != mode && (setOldWidth(), explore())
}

function listenToggle() {
    1 != mode && listen()
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
    "webkitSpeechRecognition" in window ? (microphoneListenMode = !0, document.getElementById("mic"), recognition = new webkitSpeechRecognition, recognition.continuous = !0, recognition.requiredConfidence = .1, recognition.interimResults = !1, recognition.lang = language, alert(recognition.lang), recognition.onstart = function () {
        console.log("on start");
        hideMessage();
        var b = document.getElementById("mic");
        launchMicHTML = b.innerHTML;
        b.innerHTML = generateButtonHtml("mic_record.png", 38, 38, "margin-left: 20px;padding:2px 4px")
    },
        recognition.onresult = function (b) {
            for (var c = b.resultIndex; c < b.results.length; ++c) b.results[c].isFinal && (final_transcript += b.results[c][0].transcript, console.log("result in"), postPlayBeforeSelectSpeakingQuiz || playLetter())
        }, recognition.onerror = function (b) {
        console.log("" + b.error)
    }, recognition.onend = function () {
        console.log("on end");
        setUpMicrophoneLaunchIcon();
        advanceButton.focus()
    }, final_transcript = "", console.log("prepare for launch"), recognition.start(), displayMessage("Please use headphones when using this feature.  Say the word for the selected image. Your voice will be detected and the correct answer will be spoken",
        1E4)) : upgrade()
}

var useLocalPoints = !0, pointsDiv;

function initPoints(b) {
    points = parseInt(b);
    pointsDiv = document.getElementById("points");
    pointsDiv.innerHTML = points
}

var userDiv, gameActivated = !1;

function createUserDiv() {
    "1" === localStorage.getItem("game") && "undefined" != typeof language && "en" == language && (gameActivated = !0, userDiv = document.createElement("div"), userDiv.id = "user_div", userDiv.setAttribute("style", "position:absolute;right: 0px; top:0;padding:6px;text-align:right;"), pointsDiv = document.createElement("div"), pointsDiv.id = "points", pointsDiv.addEventListener("click", function () {
        window.location.href = "/user/points.jsp?lang=" + language
    }), document.body.appendChild(pointsDiv))
}

function userCallback() {
    if (4 == req.readyState && 200 == req.status) {
        var b = document.getElementsByTagName("body")[0];
        b = null != target && "en" !== target ? "?target=" + target : "";
        if ("{}" != req.responseText) {
            var c = req.responseText, d = c.indexOf("^");
            if (-1 != d) {
                var e = c.substr(0, d);
                c.substr(d + 1, c.length - 1)
            } else e = c;
            c = document.createElement("div");
            c.id = "user2Button";
            c.className = "optionsButton";
            c.addEventListener("click", function () {
                toggleDisplayOptions(event, "user2", !0)
            }, !1);
            c.innerHTML = +e + '<img src="static/images/down_arrow.png" width="10" height="6">';
            e = document.createElement("div");
            e.setAttribute("class", "options");
            e.id = "user2";
            c = document.createElement("div");
            c.setAttribute("onclick", "location.href='/user/account.jsp" + b + "'");
            c.setAttribute("class", "option link");
            c.innerHTML = savedWords;
            e.appendChild(c);
            c = document.createElement("div");
            c.innerHTML = logout;
            c.setAttribute("class", "option link");
            c.setAttribute("onclick", "location.href='/user/logout.jsp" + b + "'");
            e.appendChild(c);
            b = document.getElementsByTagName("body")[0];
            b.appendChild(e);
            registerVisit()
        }
    }
}

function loadUserInfo() {
    "undefined" != typeof XMLHttpRequest ? req = new XMLHttpRequest : window.ActiveXObject && (req = new ActiveXObject("Microsoft.XMLHTTP"));
    req.open("GET", "/user/getUserName.jsp", !0);
    req.onreadystatechange = userCallback;
    req.send(null)
}

var visitId, registeredVisit = !1, alreadyScored;

function visitRegistered() {
    if (4 == req.readyState && 200 == req.status) {
        var b = req.responseText, c = b.indexOf("-");
        -1 != c ? (visitId = b.substr(0, c), b = b.substr(c + 1, b.length - 1), alreadyScored = [], alreadyScored.push.apply(alreadyScored, b.split(",").map(Number))) : (visitId = b, alreadyScored = []);
        registeredVisit = !0
    }
}

function registerVisit() {
    if ("undefined" != typeof lgname) {
        var b = "/user/visit.jsp?c=" + lgname + "&n=" + number + "&t=" + target + "&l=" + language;
        "undefined" != typeof XMLHttpRequest ? req = new XMLHttpRequest : window.ActiveXObject && (req = new ActiveXObject("Microsoft.XMLHTTP"));
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
        null != c ? (awardArray = JSON.parse(c), "undefined" == typeof awardArray[language] && (awardArray[language] = [])) : (awardArray = {}, awardArray[language] = []);
        awardArray[language].push(b);
        b = JSON.stringify(awardArray);
        localStorage.setItem("awards", b)
    }

    function c() {
        var c = !1;
        "undefined" != typeof award && (d(lgname, award.desc), b(lgname), c = !0);
        if ("undefined" !== typeof group) {
            for (var e = "g-" + group.name + "-" + language, f = localStorage.getItem(e), g = "", h = 0; h <
            group.total; h++) g += "1";
            if (null == f) for (f = "", h = 0; h < group.total; h++) f = h == group.index ? f + "1" : f + "0"; else h = 0, h = f.substring(0, group.index) + 1, group.total > group.index + 1 && (h += f.substring(group.index + 1, f.length)), f = h;
            localStorage.setItem(e, f);
            f == g && (b(group.name), c ? addOnCloseCallback(function () {
                d(group.name, group.desc)
            }) : d(group.name, group.desc))
        }
    }

    function d(b, c) {
        if (gameActivated) {
            var d = document.createElement("div");
            c = "<div>" + c + "</div>\t";
            d.id = "award";
            d.style.height = "300px";
            d.style.top = 0;
            d.style.backgroundColor =
                "#4b7aa4";
            d.style.display = "table-cell";
            d.style.verticalAlign = "middle";
            d.style.bottom = 0;
            var e = document.createElement("div"), f = document.createElement("div");
            f.style.height = "100%";
            f.style.verticalAlign = "middle";
            e.id = "modalPage";
            document.body.appendChild(e);
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
                '<img src="/images/awards/' + (b + ".png") + '"  /><div style="width:200px; margin:auto">' + c + '</div><div style="margin-top:10px;"><img src="static/images/x.png" width="40" height="40" /></div>';
            document.body.appendChild(d);
            createAudioElement("victory");
            playAudio("victory")
        }
    }

    function e() {
        var b = document.getElementById("listen"), c = b.innerHTML;
        b.style.paddingRight = "24px";
        b.innerHTML = c + B
    }

    function f() {
        var b = document.getElementById("speak");
        b.style.paddingRight = "28px";
        b.innerHTML += B
    }

    function g(b, c) {
        var d =
            localStorage.getItem(q);
        if (null != d) {
            var e = parseInt(d);
            e += b;
            localStorage.setItem(q, "" + e)
        } else localStorage.setItem(q, b);
        gameActivated && (pointsDiv.innerHTML = e, 0 < b && (c += " You just earned " + b + " points."));
        displayMessage(c, 4E3)
    }

    var h = !1, l = !1, w = !1, u = null, q = "points-" + language, k = lgname + "-" + language, C = "lpoints-" + k,
        v = "spoints-" + k, x, r, m, A;
    this.resetPoints = function () {
        localStorage.clear()
    };
    this.processGroup = function () {
        c()
    };
    this.markListeningFinished = function (b) {
        t || (t = !0, g(r, b), r = 0, localStorage.setItem(v, 0), n ?
            (localStorage.setItem(k, "3"), c()) : localStorage.setItem(k, "1"), e())
    };
    var B = '<object data="/images/checkmark.svg" type="image/svg+xml" width="40px" height="40px" class="cm"> </object>';
    this.markSpeakingFinished = function (b) {
        n ? displayMessage("Starting over...", 2E3) : (n = !0, g(m, b), m = 0, localStorage.setItem(v, m), t ? (localStorage.setItem(k, "3"), c()) : localStorage.setItem(k, "2"), f())
    };
    this.removedAlreadyGuessedSpeaking = function (b) {
        var c = correctSpeakingGuesses.length;
        if (0 < c && b.length !== c) for (var d = 0; d < c; d++) {
            var e =
                b.indexOf(correctSpeakingGuesses[d]);
            b.splice(e, 1)
        }
    };
    this.startPointSavingTimer = function () {
        null == u && (u = window.setInterval(this.savePointsLocally, 1E3))
    };
    this.cancelPointSavingTimer = function () {
        clearInterval(u);
        u = null;
        this.savePointsLocally()
    };
    this.savePointsLocally = function () {
        if (h) {
            h = !1;
            if (w) {
                localStorage.setItem(v, m);
                w = !1;
                var b = JSON.stringify(correctSpeakingGuesses);
                localStorage.setItem(x, b)
            }
            l && (localStorage.setItem(C, r), l = !1, b = JSON.stringify(correctGuesses), localStorage.setItem(A, b))
        }
    };
    var n, t;
    this.loadPointsFromLocalStorage =
        function () {
            var b = localStorage.getItem(q), c = localStorage.getItem(k);
            null != c && (1 == c ? (e(), t = !0) : 2 == c ? (f(), n = !0) : 3 == c && (e(), f(), t = n = !0));
            c = localStorage.getItem(v);
            m = null != c ? new Number(c) : 0;
            c = localStorage.getItem(C);
            r = null != c ? new Number(c) : 0;
            "undefined" !== b && "NaN" !== b ? points = new Number(b) : (points = 0, localStorage.setItem(q, "0"));
            gameActivated && (pointsDiv.innerHTML = points)
        };
    this.loadListeningPointsFromLocalStorage = function () {
        A = k + "-clg";
        var b = localStorage.getItem(A);
        correctGuesses = null != b ? JSON.parse(b) : {}
    };
    this.loadSpeakingPointsFromLocalStorage = function () {
        x = k + "-csg";
        var b = localStorage.getItem(x);
        correctSpeakingGuesses = null != b ? JSON.parse(b) : []
    };
    this.recordSpeakingCorrect = function (b) {
        n || -1 != correctSpeakingGuesses.indexOf(b) || (m += 1, h = !0, correctSpeakingGuesses.push(b), w = !0)
    };
    this.recordListeningCorrect = function (b) {
        1 != correctGuesses[b] && (r += 2, h = !0, correctGuesses[b] = 1, l = !0)
    };
    this.loadPointsFromLocalStorage()
}

function toggleDisplayOptions(b, c, d) {
    if (null != options && "visible" == options.style.visibility && (options.style.visibility = "hidden", options.id == c)) return;
    for (var e = document.getElementById(c + "Button"), f = e.offsetHeight; null != e;) f += e.offsetTop, e = e.offsetParent;
    options = document.getElementById(c);
    options.style.top = f + "px";
    d && (options.style.right = 0);
    options.style.visibility = "visible";
    b.cancelBubble = !0;
    b.stopPropagation && b.stopPropagation()
}

function getDifficultyDisplayString() {
    return 0 === currentDifficulty ? beginner : 1 === currentDifficulty ? intermediate : advanced
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
    "undefined" !== typeof difficulty && (b.innerHTML = difficulty);
    b.style.marginTop = "10px";
    b.style.borderBottom = "1px solid black";
    d.appendChild(b);
    createRadioRow("difficulty", "b", d, beginner);
    createRadioRow("difficulty", "i", d, intermediate);
    createRadioRow("difficulty", "a", d, advanced);
    createOptionRowFromCookie("offensive", d, showOffensiveContent, toggleOffensive);
    b = localStorage.getItem("difficulty");
    b = "0" === b ? document.getElementById("b") : "1" === b ? document.getElementById("i") : document.getElementById("a");
    b.checked = !0;
    var e = document.createElement("div");
    e.id = "x-out2";
    document.body.appendChild(e);
    hidePreferences = function (b) {
        document.body.removeChild(d);
        document.body.removeChild(e);
        document.body.removeChild(c);
        hidePreferences = null
    };
    c.addEventListener("click", hidePreferences, !1);
    e.addEventListener("click", hidePreferences, !1)
}

function createOptionRow(b, c, d, e) {
    var f = document.createElement("div");
    f.id = c + "row";
    b.appendChild(f);
    b = document.createElement("input");
    b.type = "checkbox";
    b.name = c;
    b.id = c;
    b.checked = e;
    b.style.pointerEvents = "none";
    f.appendChild(b);
    c = document.createElement("label");
    c.innerHTML = d;
    f.appendChild(c);
    return f
}

function createOptionRowFromStorage(b, c, d, e) {
    var f = localStorage.getItem(b);
    null == f || "1" == f ? (c = createOptionRow(c, b, d, !0), document.getElementById(b).checked = !0) : c = createOptionRow(c, b, d, !1);
    c.addEventListener("click", function () {
        var c = document.getElementById(b), d = e(!c.checked);
        c.checked ? (c.checked = !1, d && localStorage.setItem(b, "0")) : (c.checked = !0, d && localStorage.setItem(b, "1"))
    }, !1)
}

function createOptionRowFromCookie(b, c, d, e) {
    var f = !1, g = getCookie("prefs3");
    null != g && "1" == g.substring(2, 3) && (f = !0);
    c = createOptionRow(c, b, d, f);
    c.style.borderTop = "1px solid black";
    c.addEventListener("click", function () {
        var c = document.getElementById(b), d = g.substring(0, 2);
        e(!f, d);
        c.checked = c.checked ? !1 : !0
    }, !1)
}

function createRadioRow(b, c, d, e) {
    var f = null, g = document.createElement("div");
    g.id = c + "-row";
    d.appendChild(g);
    d = document.createElement("input");
    d.type = "radio";
    d.name = b;
    d.id = c;
    d.value = b;
    g.appendChild(d);
    b = document.createElement("label");
    b.innerHTML = e;
    g.appendChild(b);
    g.addEventListener("click", function () {
        "b-row" == g.id ? (f = document.getElementById("b"), localStorage.setItem("difficulty", "0"), activeBeginnersMode()) : "i-row" == g.id ? (f = document.getElementById("i"), localStorage.setItem("difficulty", "1"), activeIntermediateMode()) :
            "a-row" == g.id && (f = document.getElementById("a"), localStorage.setItem("difficulty", "2"), activeAdvancedMode());
        updateDifficultyDisplay();
        f.checked = !0
    }, !1)
};
