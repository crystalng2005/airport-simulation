// big simulation sittings
let UPS = 1; // staring default update rate
const maxUPS = 10; // the maximum number of UPS that the simulation will allow
const TICK_MINUTES = 5; // minutes per tick, must match backend


// planes sittings
let planeSpawnSlideDuration = 0.3 / UPS; //in sec
let planeRunwaySlideDuration = 0.5 / UPS; //in sec
let planeFadeOutDuration = 0.2 / UPS; //in sec
let planesQueueSlideDuration = 1 / UPS; //in sec
const planeSize = 95;
const planeEmergencyColor = 'linear-gradient(0, #ff7070, #d13a3a)';

// plane info screen sittings
const showInfoScreenAllTime = false;


// global tracking variables section. 
let numberOfRunways = 10; 
let changeUPS_nextUpdate = false;
let newUPS = UPS;
let turnSimulationOFF = false; // simulation stops if its true, runs otherwise
let simulationHasStoped = false;
let simulationTick = 0;


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

/**
 * Starts the simulation's loop.
 * @returns {void}
 */
async function startSimulation(){
 
  simulationTick++;

  // ask the back-end to calculate update
  await goToNextUpdate();

  // visualize current Update
  await simulateUpdate();

  // if the simulation hasn't ended
  if(!(await stopSimulationCheck())){

    // if the UPS got updated by the user in current Update
    if(changeUPS_nextUpdate){
      // update the UPS value and all other variables that depends on UPS 
      changeUPS_nextUpdate = false;
      UPS = newUPS;
      planeSpawnSlideDuration = 0.3 / UPS; 
      planeRunwaySlideDuration = 0.5 / UPS; 
      planeFadeOutDuration = 0.2 / UPS; 
      planesQueueSlideDuration = 1 / UPS; 
    }
    
    // if simulation is On, go to next Update after waiting for 1/UPS seconds
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

/**
 * Visualize to the screen the Back-end's result for current update.
 * @returns {void}
 */
async function simulateUpdate() {

  // get every plane action that happened for the last updat e
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
      killPlane(planeID);  
    }
  }

  updateTimer();
  await updateRunwaysStatus();

}

/**
 * Visualize the runways on the screen by representing them as div elements. 
 * @param {number} num - The number of runways
 * @returns {void}
 */
async function createRunways(num) {

  // get the runway modes from the Back-end
  const runwaysModes = await getRunwaysMode();
  // get the runways HTML container
  const container = document.getElementById("container");

  // Clear previous runwayes
  container.innerHTML = "";

  // for each created runway
  for (let i = 0; i < num; i++) {

    // create the runway and its hat
    const runway = document.createElement("div");
    runway.classList.add("runway");
    runway.id = 'runway:'+String(i + 1);

    const runwayHat = document.createElement("div");
    runwayHat.classList.add("runway-hat");

    runway.appendChild(runwayHat);
    container.appendChild(runway);

    // set the hat size by half of the runway's width
    runwayHat.style.width = (runway.getBoundingClientRect().width / 2) + 'px';
    runwayHat.style.height = runwayHat.style.width;    

    // If the runway is mixed or only accepts arriving planes.
    if(runwaysModes[i] >= 0){
      // give it a blue hat
      const runwayHatBlue = document.createElement("div");
      runwayHatBlue.classList.add("runway-hat-blue");    
      runwayHat.appendChild(runwayHatBlue);
    }
  
    // If the runway is mixed or only accepts departing planes.
    if(runwaysModes[i] <= 0){
      // give it a red hat
      const runwayHatRed = document.createElement("div");
      runwayHatRed.classList.add("runway-hat-red");    
      runwayHat.appendChild(runwayHatRed);
    }
  }
}

/**
 * Creates a plane div element inside one of the Queues.
 * @param {number} planeID - The plane's Callsign
 * @param {boolean} isArrival - True if the created plane is in the Holding-Pattern Q, otherwise, the plane is in the Take-Off Q
 * @returns {void}
 */
function spawnPlane(planeID, isArrival){

  // create the div element
  const plane = document.createElement("div");

  // fill it up with its values 
  plane.id = 'plane:'+String(planeID);
  plane.classList.add("planes");
  plane.innerHTML = planeID;
  plane.style.animationDuration = planeSpawnSlideDuration + 's';
  plane.style.width = (planeSize) + 'px';
  plane.style.height = plane.style.width

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
  
  // get the correct Queue div element based on "isArrival" value
  let wrapper;
  if(isArrival){    
    wrapper = document.querySelector('.holding-pattern-plane-wrapper');
    plane.style.transform = "translateX(150vw)";
  }
  else{
    wrapper = document.querySelector('.take-off-plane-wrapper');
    plane.style.transform = "translateX(-150vw)";
  }
  // add the plane to the queue
  wrapper.appendChild(plane);
}

/**
 * Starts the plane slide to the runway animation.
 * @param {number} planeID - The plane's Callsign
 * @param {number} runwayID - The runway Index
 * @returns {void}
 */
function movePlaneToRunway(planeID, runwayID){

  const plane = document.getElementById('plane:' + planeID);
  const runway = document.getElementById('runway:' + runwayID);

  if (!plane || !runway) return;

  // get positions before moving
  const planeRect = plane.getBoundingClientRect();
  const runwayRect = runway.getBoundingClientRect();

  // slide the planes in front that are behind the moved plane
  slideQueuePlanes(plane);
  
  // append plane to runway
  runway.appendChild(plane);

  // compute relative position **inside runway**
  const relativeLeft = planeRect.left - runwayRect.left;
  const relativeTop = planeRect.top - runwayRect.top;

  // set absolute positioning relative to runway
  plane.style.position = 'absolute';
  plane.style.left = `${relativeLeft}px`;
  plane.style.top = `${relativeTop}px`;
  plane.style.margin = 0;
  plane.style.transform = 'none'; 

  // calculate runway center positions values
  const borderWidth = 2 * parseFloat(window.getComputedStyle(plane).borderTopWidth);

  const horizontalShift = (runwayRect.width-planeRect.width-borderWidth)/2;
  const verticalShift = (runwayRect.height-planeRect.height-borderWidth)/2;

  // set the plane animation
  plane.animate(
    [
      { left: `${relativeLeft}px`, top: `${relativeTop}px` }
      ,{ left: `${horizontalShift}px`, top: `${verticalShift}px`}
    ],
    {
      duration: planeRunwaySlideDuration * 1000,
      fill: 'forwards',
      easing: 'ease-in-out'
    }
  );
}

/**
 * Slides all planes that are behind a leaving plane to their new correct positions.
 * @param {object} plane - The leaving plane's HTML div element
 * @returns {void}
 */
function slideQueuePlanes(plane){

  const wrapper = plane.parentElement;
  const allPlanes = wrapper.children;
  const planes = []; // the planes that are behind "plane"
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

/**
 * Kill/Remove a plane from the screen.
 * @param {number} planeID - The plane's Callsign
 * @returns {void}
 */
function killPlane(planeID){

  // get the plan div
  const plane = document.getElementById('plane:' + planeID);

  // give the plane a fade-out animation and start it
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

  // after the fading, remove the plane div
  killAnimation.onfinish = () => {
    
    // if the plane got killed in one of the queues
    if(plane.parentElement.className != 'runway'){
      slideQueuePlanes(plane);
    }

    plane.remove();
  };
}

/**
 * Update the Timer on the top left of the screen to the latest time.
 * @returns {void}
 */
function updateTimer(){

  const timer = document.querySelector(".timer");

  // Calculate elapsed simulated time from tick count
  let totalMinutes = simulationTick * TICK_MINUTES;
  let totalHours = Math.floor(totalMinutes / 60);
  let numOfMinutes = totalMinutes % 60;
  let totalDays = Math.floor(totalHours / 24);
  totalHours = totalHours % 24;

  if(numOfMinutes < 10) numOfMinutes = '0'+numOfMinutes;
  else numOfMinutes = ''+numOfMinutes;

  if(totalHours < 10) totalHours = '0'+totalHours;
  else totalHours = ''+totalHours;

  if(totalDays < 10) totalDays = '0'+totalDays;
  else totalDays = ''+totalDays;

  const timeStr = (totalDays)+':'+(totalHours)+':'+(numOfMinutes);

  timer.innerHTML = (timeStr);
}

/**
 * Change the status of a Plane to an Emergency by change its color to red.
 * @param {number} planeID - The plane's Callsign
 * @returns {void}
 */
function letPlaneHaveEmergency(planeID){
  const plane = document.getElementById('plane:' + planeID);
  if (!plane) return;
  plane.style.background = planeEmergencyColor;
}

/**
 * Check the status of all Runways for the current simulation update and change their Border color to red if they have an Emergency or to black if it's operational.
 * @returns {void}
 */
async function updateRunwaysStatus(){

  // get the list of their status
  const runwayStatus = await getRunwaysStatus();

  // stop if the list is empty
  if (!runwayStatus) 
    return;
  

  // for each runway
  for(let i = 0; i < numberOfRunways; i++){
    const runway = document.getElementById('runway:'+String(i + 1));
    if (!runway) continue;

    // let the runway have a black border if it's operational
    if(runwayStatus[i])
      runway.style.border = "3px solid rgb(0, 0, 0)";

    // let the runway have a red border if it's operational
    else
      runway.style.border = "3px solid rgb(209, 58, 58)";
  }
}

/**
 * Update the Plane hover Info Screen Content to the Choosen Plane.
 * @param {number} planeID - The plane's Callsign
 * @returns {void}
 */
async function updateInfoScreenContent(planeID){
  
  // get the info screen div
  const planeInfoScreen = document.querySelector('.display-info-screen');

  // get the Values of the Plane
  const air = await getAircraft(planeID);

  // update the info screen

  if (air) {
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
    
  else{
    planeInfoScreen.innerHTML = `Aircraft ${planeID} Info: unavailable`;
    return;
  }
}

/**
 * Returns a list from the back-end of all plane actions for the current update, where each element is a list of size 2 that holds the plane's callsign and its action.
 * @returns {(number|string)[][]}
 */
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

/**
 * Tells the back-end to calculate the next update.
 * @returns {void}
 */
async function goToNextUpdate(){
  try {
    const response = await fetch('/api/next-frame', { method: 'POST' });
    const data = await response.json();
    if (data.success) {
      console.log('Update advanced');
    }
  } 
  catch (error) {
    console.error('Error advancing Update:', error);
  }
}

/**
 * Returns a plane's information as an Aircraft Object.
 * @param {number} planeCallSign - The plane's Callsign
 * @returns {Aircraft}
 */
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

/**
 * Return true if the simulation has ended.
 * @returns {boolean}
 */
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

/**
 * Returns the number of Runways the user had specified.
 * @returns {number}
 */
function getNumberOfRunways(){
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

/**
 * Returns the current status of all runways as a list of booleans, where list[i] value represents the runway_i status.
 * @returns {boolean[]}
 */
function getRunwaysStatus(){
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
}

/**
 * Returns the modes of all runways as a list of number, where list[i] value represents the runway_i Mode
 * 
 * list[i] =  1 -> Only arrivals Mode
 * 
 * list[i] =  0 -> Mixed Mode
 * 
 * list[i] = -1 -> Only departures Mode
 * @returns {number[]}
 */
function getRunwaysMode(){
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
}