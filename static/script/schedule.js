function getTime(){
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    fetch('/time')

    .then(response => response.json())
    .then(data=>{
    
        if(data.status != 200){
            console.log("Get time error - " + data.error + " | " + data.status);
        }else{
            data = data.data;

            schedule = data[0];
            duration = data[1];

            duration = duration['duration'];

            const durationElement = document.getElementById('durationTime');

            durationElement.value = duration;

            for (let day in days){
                let element = document.getElementById(days[day].toLowerCase() + "Time")
                if (schedule[days[day]] == "false"){
                    element.style.backgroundColor = "#FF0044";
                } else {
                    element.value = schedule[days[day]];
                };
            }
        }
    })
}

function updateJson(){
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    const durationElement = document.getElementById('durationTime');

    let data = [];

    let time = [];

    let duration = durationElement.value;

    for (let day in days){
        let element = document.getElementById(days[day].toLowerCase() + "Time")
        let selectTime = element.value;
        if (selectTime.length < 1){
            time.push("false");
        } else {
            time.push(selectTime);
        }
    }

    data.push(time);
    data.push(duration);

    let url = "/process-data"
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        let strResponse = "Error: no response";
        if (this.readyState == 4 && this.status == 200) {
            strResponse = JSON.parse(this.responseText);
            if (strResponse.status != 200){
                alert("Failed to update")
                console.log("Get time error - " + strResponse.data + " | " + strResponse.status);
            } else {
                alert("Updated times!")
                window.location.replace("/");
            }
        }
    };
    xhttp.open("PUT", url, true);
    // Converting JSON data to string
    var dataSend = JSON.stringify(data);
    // Set the request header i.e. which type of content you are sending
    xhttp.setRequestHeader("Content-Type", "application/json");
    //send it
    xhttp.send(dataSend);

}

setTimeout(() => {
    getTime()
  }, 1000);