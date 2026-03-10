// big simulation sittings
let UPS = 1; // staring default update rate
const maxUPS = 10; // the maximum number of UPS that the simulation will allow
let simulationTick = 0;
const TICK_MINUTES = 5; // minutes per tick, must match backend

// runways sittings
const runway_size = 100;
const runway_border_thinkness = 4;
const runwayEmergencyColor = 'linear-gradient(0, #ff7070, #d13a3a)';

// planes sittings
let planeSpawnSlideDuration = 0.3 / UPS; //in sec
let planeRunwaySlideDuration = 0.5 / UPS; //in sec
let planeFadeOutDuration = 0.2 / UPS; //in sec
let planesQueueSlideDuration = 1 / UPS; //in sec
const planeEmergencyColor = 'linear-gradient(0, #ff7070, #d13a3a)';

// plane info screen sittings
const showInfoScreenAllTime = false;


// global variables section. 
let numberOfRunways = 10; 
let changeUPS_nextUpdate = false;
let newUPS = UPS;
let turnSimulationOFF = false; // simulation stops if its true, runs otherwise
let simulationHasStoped = false;

// If the user press some keys
document.addEventListener("keydown", function(event) {


  // stop/start the simulation temporary after pressing the spacebar
  if (event.code === "Space"){    
    if(simulationHasStoped){
      turnSimulationOFF = false;
      simulationHasStoped = false;
      startSimulation();
    }
    else
      turnSimulationOFF = true;
  }

  // if the simulation is on and the key pressed is right or left arrow
  if(!turnSimulationOFF && (event.key === "ArrowLeft" || event.key === "ArrowRight")){
    
    changeUPS_nextUpdate = true;

    // increase the UPS in next update
    if (event.key === "ArrowLeft" && newUPS > 1)
        newUPS -= 1;
    
    // decrease the UPS in next update
    if (event.key === "ArrowRight" && newUPS <= maxUPS)
      newUPS += 1;
  }  
});



// Simulation is already started by configure_simulation.js calling /start
// Just initialize the screen and begin the loop
(async function init() {
  try {
    // Get runway count from the already-running simulation
    const res = await fetch('/api/number-of-runways');
    const data = await res.json();
    if (data.success) {
      numberOfRunways = data.number;
    }
    await createRunways(numberOfRunways);
    startSimulation();
  } catch (error) {
    console.error('Error initializing simulation screen:', error);
  }
})();




// startSimulation() is now called after the /start fetch completes (see above)


// ________________________________________________________________________________________________________
// Classes Difinitions Section :
// ________________________________________________________________________________________________________
class Aircraft{
  constructor(c,o,d,i,f,e,t,a,cu){
    // this.id = ID;
    this.callsign = c;
    this.origin = o;
    this.destination = d;
    this.is_departure = i;
    this.fuel_level = f;
    this.emergency_status = e;
    this.target_time = t;
    this.actual_time = a;
    this.current_location = cu;
  }
}

// ________________________________________________________________________________________________________
// Function Difinitions Section:
// ________________________________________________________________________________________________________
async function startSimulation(){
  // ask the back-end to calculate update
  await goToNextUpdate();
  simulationTick++;

  // visualize current Update
  await simulateUpdate();

  // if the simulation hasn't ended
  if(!(await stopSimulationCheck())){

    if(changeUPS_nextUpdate){
      // update the UPS value and all other variables that depends on UPS 
      changeUPS_nextUpdate = false;
      UPS = newUPS;
      planeSpawnSlideDuration = 0.3 / UPS; 
      planeRunwaySlideDuration = 0.5 / UPS; 
      planeFadeOutDuration = 0.2 / UPS; 
      planesQueueSlideDuration = 1 / UPS; 
    }
    
    // if simulation is on, go to next Update after waiting for 1/UPS seconds
    if(!turnSimulationOFF)
      setTimeout(startSimulation,1000/UPS);

    else
      simulationHasStoped = true;
    
  } 

  // if the simulation has ended
  else {
    // go to the simulation result page
    window.location.href = '/result-screen'; 
  }
}

async function simulateUpdate() {

  let currentUpdateActions = await getCurrentUpdateActions();

  // for every plane that did something in current Update
  for(let i = 0; i<currentUpdateActions.length; i++){

    let planeID = currentUpdateActions[i][0];   
    let action = currentUpdateActions[i][1];

    // if the plane spawn in the holding pattern
    if(action == "spawnLanding"){
      // console.log("Land"+planeID)
      spawnPlane(planeID,true);
    }

    // if the plane spawn in the take-off
    else if(action == "spawnDeparture"){
      // console.log("Derp"+planeID)
      spawnPlane(planeID,false);
    }

    // if the plane got an emergency
    else if(action == "emergency"){
      // console.log("emer"+planeID)
      letPlaneHaveEmergency(planeID);  
    }
    // if the plane moved to a runway
    else if(Number.isInteger(action))
      movePlaneToRunway(planeID, action);

    // if the plane got diverted or cancelled or landed or taked-off from a runway
    // (aka the plan is done)
    else if(action == "kill"){
      // console.log("kill:"+planeID)
      killPlane(planeID);  
    }
  }

  updateTimer();
  await updateRunwaysStatus();

}

async function createRunways(num) {

  const container = document.getElementById("container");
  const runwaysModes = await getRunwaysMode();

  // Clear previous runwayes
  container.innerHTML = "";

  for (let i = 0; i < num; i++) {
    const runway = document.createElement("div");
    runway.classList.add("runway");
    runway.id = 'runway:'+String(i + 1);

    const runwayHat = document.createElement("div");
    runwayHat.classList.add("runway-hat");

    runway.appendChild(runwayHat);

    container.appendChild(runway);

    runwayHat.style.width = (runway.getBoundingClientRect().width / 2) + 'px';
    runwayHat.style.height = runwayHat.style.width;    

    if(runwaysModes[i] >= 0){
      const runwayHatBlue = document.createElement("div");
      runwayHatBlue.classList.add("runway-hat-blue");    
      runwayHat.appendChild(runwayHatBlue);
    }
  
    if(runwaysModes[i] <= 0){
      const runwayHatRed = document.createElement("div");
      runwayHatRed.classList.add("runway-hat-red");    
      runwayHat.appendChild(runwayHatRed);
    }
  }
}

// isArrival: Boolean
function spawnPlane(planeID, isArrival){

  // create a div element
  const plane = document.createElement("div");

  // fill it up with its values 
  plane.id = 'plane:'+String(planeID);
  plane.classList.add("planes");

  plane.innerHTML = planeID;

  plane.style.width = (runway_size * 0.95) + 'px';
  plane.style.height = plane.style.width

  let wrapper;

  if(isArrival){    
    wrapper = document.querySelector('.holding-pattern-plane-wrapper');
    plane.style.transform = "translateX(150vw)";
  }
  else{
    wrapper = document.querySelector('.take-off-plane-wrapper');
    plane.style.transform = "translateX(-150vw)";
  }

  plane.style.animationDuration = planeSpawnSlideDuration + 's';


  // define the mouse hover screen infor pop-up
  const planeInfoScreen = document.querySelector('.display-info-screen');

  if(!showInfoScreenAllTime){

    plane.addEventListener("mouseenter", () => {
      updateInfoScreenContent(planeID);
      planeInfoScreen.style.display = "flex";
    });

    plane.addEventListener("mouseleave", () => {
      planeInfoScreen.style.display = "none";
    });
  }

  else
    planeInfoScreen.style.display = "flex";


  // after the slide in animation is done, remove the animation from the element
  plane.addEventListener('animationend', () => {
    plane.style.transform = "none";
    plane.style.animation = 'none';
  });

  // add the plane to the queue
  wrapper.appendChild(plane);
}

function movePlaneToRunway(planeID, runwayID){

  const plane = document.getElementById('plane:' + planeID);
  const runway = document.getElementById('runway:' + runwayID);

  if (!plane || !runway) return;

  // 1. Get positions before moving
  const planeRect = plane.getBoundingClientRect();
  const runwayRect = runway.getBoundingClientRect();

  // 2. Slide the Planes before the moved one to their correct position
  slideQueuePlanes(plane);
  

  // 3. Append plane to runway
  runway.appendChild(plane);

  // 4. Compute relative position **inside runway**
  const relativeLeft = planeRect.left - runwayRect.left;
  const relativeTop = planeRect.top - runwayRect.top;

  // 5. Set absolute positioning relative to runway
  plane.style.position = 'absolute';
  plane.style.left = `${relativeLeft}px`;
  plane.style.top = `${relativeTop}px`;
  plane.style.margin = 0;
  plane.style.transform = 'none'; 

  const shift = (runwayRect.width - planeRect.width)/4;

  // 6. Animate into runway final position (0,0)
  plane.animate(
    [
      { left: `${relativeLeft}px`, top: `${relativeTop + shift}px` },
      { left: `${shift}px`, top: `${shift}px`}
    ],
    {
      duration: planeRunwaySlideDuration * 1000,
      fill: 'forwards',
      easing: 'ease-in-out'
    }
  );
}

function slideQueuePlanes(plane){

  const wrapper = plane.parentElement;
  const allPlanes = wrapper.children;
  const planes = []; // the planes that are on the left or right 
  const oldPositions = [];
  const newPositions = [];

  let condition = '';

  // if the plane is in the Holding pattern q
  if(plane.getBoundingClientRect().top < window.innerHeight/2){
    condition = '<';
  }
  else{
    condition = '>';
  }

  // get the desired planes and their old positions
  for (const p of allPlanes) {
    if(eval("plane.getBoundingClientRect().left" + condition + "p.getBoundingClientRect().left")){
      planes.push(p);
      oldPositions.push(p.getBoundingClientRect());
    }
  }

  // stop if the plane is last on the queue
  if(planes.length == 0)
    return 0;

  // remove the plane from the wrapper 
  wrapper.removeChild(plane);

  // get the new positions of all planes before plane
  for (const p of planes) {
      newPositions.push(p.getBoundingClientRect());
  }

  // calculate the move vectore for each plane
  planes.forEach((p, i) => {
    const dx = oldPositions[i].left - newPositions[i].left;
    const dy = oldPositions[i].top - newPositions[i].top;

    p.style.transform = `translate(${dx}px, ${dy}px)`;
    p.style.transition = 'none';
  });

  // double requestAnimationFrame needed for browser stuff
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      
      // start slide animation for all planes
      planes.forEach(p => {
        p.style.transition = 'transform '+planesQueueSlideDuration+'s ease';
        p.style.transform = '';
      });

      // remove the transition when they are done sliden
      planes.forEach(p => {
        p.addEventListener('transitionend', () => {
          p.style.transition = '';
        }, { once: true });
      });
    });
  });
}

function killPlane(planeID){

  const plane = document.getElementById('plane:' + planeID);

  const killAnimation = plane.animate(
    [
      { opacity: 1 },
      { opacity: 0 }
    ],
    {
      duration: planeFadeOutDuration * 1000,
      easing: 'ease-out',
      fill: 'forwards'
    }
  );

  killAnimation.onfinish = () => {
    
    // if the plane got killed in one of the queues
    if(plane.parentElement.className != 'runway'){
      slideQueuePlanes(plane);
    }

    plane.remove();

  };
}

function updateTimer(){

  const timer = document.querySelector(".timer");

  // Calculate elapsed simulated time from tick count
  let totalMinutes = simulationTick * TICK_MINUTES;

  let totalHours = Math.floor(totalMinutes / 60);
  let numOfMinutes = totalMinutes % 60;

  let totalDays = Math.floor(totalHours / 24);
  totalHours = totalHours % 24;

  if(totalHours < 10) totalHours = '0'+totalHours;
  else totalHours = ''+totalHours;

  if(totalDays < 10) totalDays = '0'+totalDays;
  else totalDays = ''+totalDays;

  if(numOfMinutes < 10) numOfMinutes = '0'+numOfMinutes;
  else numOfMinutes = ''+numOfMinutes;

  const timeStr = (totalDays)+':'+(totalHours)+':'+(numOfMinutes);

  timer.innerHTML = (timeStr);
}

function letPlaneHaveEmergency(planeID){
  const plane = document.getElementById('plane:' + planeID);
  if (!plane) return;
  plane.style.background = planeEmergencyColor;
}

async function updateRunwaysStatus(){
  const runwayStatus = await getRunwaysStatus();

  if (!runwayStatus) {
    return;
  }

  for(let i = 0; i < numberOfRunways; i++){
    const runway = document.getElementById('runway:'+String(i + 1));
    if (!runway) continue;

    if(runwayStatus[i])
      runway.style.border = "3px solid rgb(0, 0, 0)";

    else
      runway.style.border = "3px solid rgb(209, 58, 58)";//+ runwayEmergencyColor;
  }
}


// ________________________________________________________________________________________________________
// Unfinishe Function Difinitions Section:
// ________________________________________________________________________________________________________

async function updateInfoScreenContent(planeID){
  const planeInfoScreen = document.querySelector('.display-info-screen');
  const air = await getAircraft(planeID);

  if (!air) {
    planeInfoScreen.innerHTML = `Aircraft ${planeID} Info: unavailable`;
    return;
  }

  planeInfoScreen.innerHTML = `Aircraft ${planeID} Info:
    <ul>
      <li>Callsign: ${air.callsign}</li>
      <li>Origin: ${air.origin}</li>
      <li>Destination: ${air.destination}</li>
      <li>Is departure: ${air.is_departure}</li>
      <li>Fuel level: ${air.fuel_level.toFixed(1)}</li>
      <li>Emergency status: ${air.emergency_status}</li>
      <li>Target time: ${air.target_time}</li>
      <li>Actual time: ${air.actual_time}</li>
      <li>Current location: ${air.current_location}</li>
    </ul>`;
}


// should return a dictionary or a 2D list of size Nx2 where N is the 
// number of actions that happened in current Update and  
// every list inside the big list is = [planeID, action].

//  result ex: [[planeID_1, action_1],
//              [planeID_2, action_2],
//              [planeID_3, action_3],
//              [planeID_4, action_4],
//              [planeID_5, action_5]]
// where 'action' is a string or (an integer to represent a runway index)
function getCurrentUpdateActions(){
    return fetch('/api/current-frame-actions')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                return data.actions;
            }
            throw new Error('Failed to get Update actions');
        })
        .catch(error => {
            console.error('Error fetching Update actions:', error);
            return [];
        });
}

// used for the clock/timer on the top left corner
function getCurrentTime(){
    return fetch('/api/current-time')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                return new Date(data.time);
            }
            throw new Error('Failed to get current time');
        })
        .catch(error => {
            console.error('Error fetching time:', error);
            return null;
        });
}

// tells the back-end to calculate the next Update.
// i don't know if this function is needed or not
async function goToNextUpdate(){
    try {
        const response = await fetch('/api/next-frame', { method: 'POST' });
        const data = await response.json();
        if (data.success) {
            console.log('Update advanced');
        }
    } catch (error) {
        console.error('Error advancing Update:', error);
    }
}

function getAircraft(planeCallSign){
    return fetch(`/api/aircraft/${planeCallSign}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const air = data.aircraft;
                return new Aircraft(
                    air.callsign,
                    air.origin,
                    air.destination,
                    air.is_departure,
                    air.fuel_level,
                    air.emergency_status,
                    air.target_time,
                    air.actual_time,
                    air.current_location
                );
            }
            return null;
        })
    .catch(error => {
      console.error('Error fetching aircraft:', error);
      return null;
    });
}


// return true if the simulation has ended
async function stopSimulationCheck(){
  try {
    const response = await fetch('/api/simulation-finished');
    const data = await response.json();
    if (data.success) {
      return data.finished;
    }
  } catch (error) {
    console.error('Error checking simulation status:', error);
  }
  return false;
}

function getNumberOfRunways(){
  // can also access directly from simulation controller
  // call get_runway_num from simulation controller
    return fetch('/api/number-of-runways')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                return data.number;
            }
            throw new Error('Failed to get number of runways');
        })
        .catch(error => {
            console.error('Error fetching number of runways:', error);
            return null;
        });
}

// returns a list of booleans where list[i] value represents the runway_i status
// list[i] = true of the runway is operational false otherwise
// output ex: if the total number of runways is 6 then the output is for example = [true, false, true, true, true, false] -> sooo, both the second and last runway are offline 
function getRunwaysStatus(){
  // call get_runway_statuses from the simulation controller class on the simulation object

    return fetch('/api/runway-statuses')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                return data.status;
            }
            throw new Error('Failed to get runway statuses');
        })
        .catch(error => {
            console.error('Error fetching statuses:', error);
            return null;
        });
  // return [true, true, true, true, true, true, true, true, true]
}

// returns a list where list[i] value represents the runway_i Mode
// list[i] = -1 -> the runway is for Take-off only
// list[i] =  0 -> the runway is for Both Modes
// list[i] =  1 -> the runway is for Arrival only
// output ex: if the total number of runways is 6 then the output is for example = [1, 0, -1, 1, 0, 1] 
function getRunwaysMode(){
  // call get_runway_modes from simulation controller
    return fetch('/api/runway-modes')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                return data.mode;
            }
            throw new Error('Failed to get runway modes');
        })
        .catch(error => {
            console.error('Error fetching modes:', error);
            return null;
        });
  // return [1,1,-1,1,0,1,1,1,1]
}

async function getReport(){
  try {
    const response = await fetch('/api/report');
    const data = await response.json();

    if (!data.success) {
      console.error('Failed to get report:', data.errors || data.error);
      return null;
    }

    return data.report;
  } catch (error) {
    console.error('Error fetching report:', error);
    return null;
  }
}

function showReport(report){
  if (!report) return;

  // For Turki to change
  const reportBox = document.querySelector('.report-container');
  if (!reportBox) {
    console.log('Final report:', report);
    return;
  }

  reportBox.innerHTML = `
    <h3>Simulation Report</h3>
    <p>Total planes: ${report.total_planes}</p>
    <p>Diversions: ${report.diversions}</p>
    <p>Cancellations: ${report.cancellations}</p>
    <p>Efficiency: ${report.efficiency}</p>
    <p>Avg wait: ${report.avg_wait_time}</p>
    <p>Max hold: ${report.max_hold_time}</p>
  `;
}

