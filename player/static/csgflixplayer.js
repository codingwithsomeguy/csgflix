(function () {

// TODO: one player per web page (for now), relax later
let player;
let metricStartTime;    // currently initialized before player

function initPlayer(videoFileWidth, videoFileHeight) {
    let player = {};

    player.canvas = new OffscreenCanvas(videoFileWidth, videoFileHeight);
    player.ctx = player.canvas.getContext("2d");
    player.offcanvas = new OffscreenCanvas(player.canvas.width, player.canvas.height);
    player.offCtx = player.offcanvas.getContext("2d");

    player.ctx.clearRect(0, 0, player.canvas.width, player.canvas.height);
    player.offCtx.clearRect(0, 0,
        player.offcanvas.width, player.offcanvas.height);

    player.deltaCanvas = new OffscreenCanvas(
        player.canvas.width, player.canvas.height);
    player.deltaCtx = player.deltaCanvas.getContext("2d");

    player.audioBufferSource = undefined;
    player.videoTimer = undefined;

    return player;
}

function showImageArray(useThisContext, imgArray) {
    const iData = player.offCtx.createImageData(
        useThisContext.canvas.width, useThisContext.canvas.height);
    for (let i = 0, j = 0; j < imgArray.length; ++i) {
        if ((i % 4) == 3) { // A
            iData.data[i] = 255;
        } else {    // R G B
            // disable RGB777 --> RGB888 for now
            //iData.data[i] = (imgArray[j]<<1);
            iData.data[i] = imgArray[j];
            j += 1;
        }
    }

    //console.log(iData);
    useThisContext.putImageData(iData, 0, 0);
}

function showImageArrayDelta(imgArrayI1, imgArrayDelta) {
    showImageArray(player.deltaCtx, imgArrayDelta);

    const iData = player.offCtx.createImageData(
        player.deltaCanvas.width, player.deltaCanvas.height);
    // save the non-RGBA computed image too for next frame
    const computedImage = new Uint8ClampedArray(imgArrayI1.length);
    for (let i = 0, j = 0; j < imgArrayI1.length; ++i) {
        if ((i % 4) == 3) { // A
            iData.data[i] = 255;
        } else {    // R G B
            iData.data[i] = imgArrayI1[j] ^ imgArrayDelta[j];
            computedImage[j] = imgArrayI1[j] ^ imgArrayDelta[j];
            j += 1;
        }
    }

    //console.log(iData);
    player.ctx.putImageData(iData, 0, 0);

    return computedImage;
}

function showScaledVideo(destCanvas) {
    const videoCanvasCtx = destCanvas.getContext("2d");
    const unscaledImageBM = player.canvas.transferToImageBitmap();
    videoCanvasCtx.drawImage(unscaledImageBM,
        0, 0, unscaledImageBM.width, unscaledImageBM.height,
        0, 0, destCanvas.width, destCanvas.height);
}

function rle_decode(arr) {
    // [3 17 3 8...] --> [17 17 17 8 8 8...]
    const result = [];
    for (let i = 0 ; i < arr.length ; i = i + 2) {
        const repetition_count = arr[i];
        const symbol = arr[i+1];
        for (let j = 0 ; j < repetition_count ; ++j) {
            result.push(symbol);
        }
    }

    return result;
}

function playAudioArray(x) {
    const aCtx = new window.AudioContext();
    const buf = aCtx.createBuffer(1, x.length, 8000);
    const bufChan = buf.getChannelData(0);
    for (let i = 0; i < x.length; ++i) {
        bufChan[i] = (x[i] - 128) / 128.0;
    }

    // only really in player to prevent it getting deallocated
    player.audioBufferSource = aCtx.createBufferSource();
    player.audioBufferSource.buffer = buf;
    player.audioBufferSource.connect(aCtx.destination);
    player.audioBufferSource.start();
}

function adjustVideoCanvases(width, height) {
    console.log("adjustVideoCanvases: " + width + ", " + height);

    if (typeof player === "undefined") {
        player = initPlayer(width, height);
    }

    player.canvas.width = width;
    player.canvas.height = height;

    player.offcanvas.width = width;
    player.offcanvas.height = height;

    player.deltaCanvas.width = width;
    player.deltaCanvas.height = height;
}

function emitMetric(metricName, value) {
    console.log(metricName, value);
    const bundle = JSON.stringify({metricName: value});
    const stringified = encodeURIComponent(bundle);
    console.log(stringified);
    fetch("/metric?d=" + stringified).then(console.log("emitMetric: sent"));
}

// TODO: This always plays from the beginning, allow "unpausing"
function play(csgson) {
    console.log("Playing CSGSON:", csgson);
    // TODO: read more of the metadata
    const videoWidth = csgson["meta"]["resolution"]["width"];
    const videoHeight = csgson["meta"]["resolution"]["height"];
    adjustVideoCanvases(videoWidth, videoHeight);

    const destCanvas = document.getElementById("videocanvas");

    // TODO: check the audio / video sync, not async streams
    playAudioArray(csgson["audio"]);

    const firstImage = rle_decode(csgson["image"]);
    let lastDelta = firstImage;

    showImageArray(player.ctx, firstImage);
    const endTime = Date.now();
    const ttp = endTime - metricStartTime;
    let i = 0;
    player.videoTimer = setInterval(function () {
            const nextDelta = rle_decode(csgson["deltas"][i]);
            lastDelta = showImageArrayDelta(lastDelta, nextDelta);
            showScaledVideo(destCanvas);
            //console.log(lastDelta);
            //lastDelta = nextDelta;

            i += 1;
            // TODO: check this is not off by one
            if (i >= csgson["deltas"].length) {
                clearInterval(player.videoTimer);
            }
        //}, 1000);
        }, 33);
    emitMetric("ttp", ttp);
}

function fetchAndPlay(url) {
    // TODO: consider ways to better associate playback / fetch metrics
    metricStartTime = Date.now();
    fetch(url).then(x => x.json()).then(play);
}

function stopPlaying() {
    console.log("stopping");
    if (player && player.videoTimer) {
        clearInterval(player.videoTimer);
    }

    if (player && player.audioBufferSource) {
        player.audioBufferSource.stop();
    }
}


const CSGFlixPlayer = {
    "fetchAndPlay": fetchAndPlay,
    "stopPlaying": stopPlaying
};

window.CSGFP = CSGFlixPlayer;

})();
