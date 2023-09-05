function loadable(){
    getCurrentData();
    getStatus();
};


function getStatus(){
    let statusText = document.getElementById("status");
    fetch('/systemState')

    .then(response => response.json())
    .then(data=>{
    
        if(data.status != 200){
            statusText.style.color = "#FF0044";
            statusText.innerHTML = "Crashed";
            console.log("Get status error - " + data.error + " | " + data.status);
        }else{
            if (data.error == false){
                if (data.data == true) {
                    statusText.innerHTML = "Running";
                    statusText.style.color = "#06a85c";
                } else {
                    statusText.innerHTML = "Stopped";
                    statusText.style.color = "black";
                }
            }else{
                statusText.innerHTML = "Crashed";
                statusText.style.color = "#FF0044";
                console.log("Status error - " + data.error + " | " + data.status)
            }
        }
    })
}

function getCurrentData(){
    fetch('/currentData')

    .then(response => response.json())
    .then(data=>{
    
        if(data.status != 200){
            console.log("Get status error - " + data.data + " | " + data.status);
        }else{
            displayCurrentData(data.data);
        };
    });
};

function displayCurrentData(data){
    // data = [watering, autowatering, indoorHumid, indoorTemp, outsideHumid, outsideTemp, boxHumid, boxTemp, cpuTemp, cpuFreq, usedDisk, fanSpeed, window]

    const indoorHumid = document.getElementById("indoorHumid");
    const indoorTemp = document.getElementById("indoorTemp");
    const outsideHumid = document.getElementById("outsideHumid");
    const outsideTemp = document.getElementById("outsideTemp");
    const boxHumid = document.getElementById("boxHumid");
    const boxTemp = document.getElementById("boxTemp");
    const cpuTemp = document.getElementById("cpuTemp");
    const cpuFreq = document.getElementById("cpuFreq");
    const storage = document.getElementById("storage");
    const fanSpeed = document.getElementById("fanSpeed");

    const watering = document.getElementById("watering");
    const autoWatering = document.getElementById("autoWatering");
    const window = document.getElementById("window");

    const indoorHumidBar = document.getElementById('indoorHumidBar');
    const outsideHumidBar = document.getElementById('outsideHumidBar');
    const boxHumidBar = document.getElementById('boxHumidBar');
    const indoorTempBar = document.getElementById('indoorTempBar');
    const outsideTempBar = document.getElementById('outsideTempBar');
    const boxTempBar = document.getElementById('boxTempBar');
    const cpuTempBar = document.getElementById('cpuTempBar');
    const cpuFreqBar = document.getElementById('cpuFreqBar');
    const storageBar = document.getElementById('storageBar');
    const fanSpeedBar = document.getElementById('fanSpeedBar');

    indoorHumid.innerHTML = data[2]+"%";
    indoorHumidBar.dataset.value = data[2];

    indoorTemp.innerHTML = data[3]+"°C";
    let indoorTempPer = data[3] * 3.3;
    indoorTempBar.dataset.value = indoorTempPer;

    outsideHumid.innerHTML = data[4]+"%";
    outsideHumidBar.dataset.value = data[4];

    outsideTemp.innerHTML = data[5]+"°C";
    let outsideTempPer = data[5] * 3.3;
    outsideTempBar.dataset.value = outsideTempPer;

    boxHumid.innerHTML = data[6]+"%";
    boxHumidBar.dataset.value = data[6];


    boxTemp.innerHTML = data[7]+"°C";
    let boxTempPer = data[7] * 3.3;
    boxTempBar.dataset.value = boxTempPer;

    cpuTemp.innerHTML = data[8]+"°C";
    let cpuTempPer = data[8]/60 * 100;
    cpuTempBar.dataset.value = cpuTempPer;


    cpuFreq.innerHTML = data[9]+"Mhz";
    let cpuFreqPer = data[9]/1800 * 100;
    cpuFreqBar.dataset.value = cpuFreqPer;

    storage.innerHTML = data[10]+"GB";
    let storagePer = data[10]/64 * 100;
    storageBar.dataset.value = storagePer;

    fanSpeed.innerHTML = data[11]+"%";
    fanSpeedBar.dataset.value = data[11];


    const indoorHumidBar_value = parseInt(indoorHumidBar.getAttribute('data-value'));
    indoorHumidBar.style.setProperty('--value', indoorHumidBar_value);
    const outsideHumidBar_value = parseInt(outsideHumidBar.getAttribute('data-value'));
    outsideHumidBar.style.setProperty('--value', outsideHumidBar_value);
    const boxHumidBar_value = parseInt(boxHumidBar.getAttribute('data-value'));
    boxHumidBar.style.setProperty('--value', boxHumidBar_value);

    const indoorTempBar_value = parseInt(indoorTempBar.getAttribute('data-value'));
    indoorTempBar.style.setProperty('--value', indoorTempBar_value);
    const outsideTempBar_value = parseInt(outsideTempBar.getAttribute('data-value'));
    outsideTempBar.style.setProperty('--value', outsideTempBar_value);
    const boxTempBar_value = parseInt(boxTempBar.getAttribute('data-value'));
    boxTempBar.style.setProperty('--value', boxTempBar_value);
    const cpuTempBar_value = parseInt(cpuTempBar.getAttribute('data-value'));
    cpuTempBar.style.setProperty('--value', cpuTempBar_value);

    const cpuFreqBar_value = parseInt(cpuFreqBar.getAttribute('data-value'));
    cpuFreqBar.style.setProperty('--value', cpuFreqBar_value);
    const storageBar_value = parseInt(storageBar.getAttribute('data-value'));
    storageBar.style.setProperty('--value', storageBar_value);
    const fanSpeedBar_value = parseInt(fanSpeedBar.getAttribute('data-value'));
    fanSpeedBar.style.setProperty('--value', fanSpeedBar_value);


    if (data[0] == true){
        watering.innerHTML = "Running";
        watering.classList.remove("loading");
        watering.classList.remove("off");
        watering.classList.add("on");
    } else {
        watering.innerHTML = "Stopped";
        watering.classList.remove("loading");
        watering.classList.remove("on");
        watering.classList.add("off");
    }

    if (data[1] == true){
        autoWatering.innerHTML = "Running"
        autoWatering.classList.remove("loading");
        autoWatering.classList.remove("off");
        autoWatering.classList.add("on");
    } else {
        autoWatering.innerHTML = "Stopped";
        autoWatering.classList.remove("loading");
        autoWatering.classList.remove("on");
        autoWatering.classList.add("off");
    }

    if (data[12] == true){
        window.innerHTML = "Open";
        window.classList.remove("loading");
        window.classList.remove("off");
        window.classList.add("on");
    } else {
        window.innerHTML = "Closed";
        window.classList.remove("loading");
        window.classList.remove("on");
        window.classList.add("off");
    }
}

function resetBtn(){
    let startBtn = document.getElementById("startBtn");
    let stopBtn = document.getElementById("stopBtn");

    startBtn.innerHTML = "Start";
    startBtn.classList.remove("buttonFail");
    startBtn.classList.remove("buttonComplete");
    startBtn.classList.remove("buttonWait");
    startBtn.classList.add("buttonOff");

    stopBtn.innerHTML = "Stop";
    stopBtn.classList.remove("buttonFail");
    stopBtn.classList.remove("buttonComplete");
    stopBtn.classList.remove("buttonWait");
    stopBtn.classList.add("buttonOff");
}

function water(value){
    let startBtn = document.getElementById("startBtn");
    let stopBtn = document.getElementById("stopBtn");

    if (value == true){
        startBtn.classList.remove("buttonComplete");
        startBtn.classList.remove("buttonOff");
        startBtn.classList.remove("buttonFail");
        startBtn.classList.add("buttonWait");
        startBtn.innerHTML = "Wait";
    } else {
        stopBtn.classList.remove("buttonComplete");
        stopBtn.classList.remove("buttonOff");
        stopBtn.classList.remove("buttonFail");
        stopBtn.classList.add("buttonWait");
        stopBtn.innerHTML = "Wait";

    }
    

    fetch('/water/' + value)

    .then(response => response.json())
    .then(data=>{
    
        if(data.status != 200){
            if (value == true){
                startBtn.classList.remove("buttonComplete");
                startBtn.classList.remove("buttonWait");
                startBtn.classList.remove("buttonOff");
                startBtn.classList.add("buttonFail");
                startBtn.innerHTML = "Failed";
            }else {
                stopBtn.classList.remove("buttonComplete");
                stopBtn.classList.remove("buttonWait");
                stopBtn.classList.remove("buttonOff");
                stopBtn.classList.add("buttonFail");
                stopBtn.innerHTML = "Failed";
            }
            console.log("Start error - " + data.data + " | " + data.status);
        }else{
            if (value == true){
                startBtn.classList.remove("buttonOff");
                startBtn.classList.remove("buttonWait");
                startBtn.classList.remove("buttonFail");
                startBtn.classList.add("buttonComplete");
                startBtn.innerHTML = "Running";
            } else {
                stopBtn.classList.remove("buttonOff");
                stopBtn.classList.remove("buttonWait");
                stopBtn.classList.remove("buttonFail");
                stopBtn.classList.add("buttonComplete");
                stopBtn.innerHTML = "Stopped";
            }
        }
        getCurrentData();
        setTimeout(() => {
            resetBtn()
          }, 3000); 
    })
    getStatus()
}

setTimeout(() => {
    loadable()
  }, 1000);
setInterval(loadable, 10000);