// runways sittings
const runway_size = 100;
const runway_border_thinkness = 4;
const numberOfRunways = 5;

// planes sittings
const planeSpawnSlideDuration = 1; //in sec
const planeRunwaySlideDuration = 1; //in sec
const planeFadeOutDuration = 0.5 //in sec
const planesQueueSlideDuration = 1 //in sec
const planeEmergencyColor = 'linear-gradient(0, #ff7070, #d13a3a)';

// plane info screen sittings
const showInfoScreenAllTime = false;


// const container = document.getElementById("container");

//call resizeCanvas() if the windo size is changing
window.addEventListener("resize", resizeWindoUpdate);

// resizeWindoUpdate(); // initial sizing

createRunways(numberOfRunways);


// updateTimer(1);


// TEST :::::::::::::
spawnPlane(9, false)

for(let i =0 ;i<10;i++){
  spawnPlane(i+10, false);
  spawnPlane(i+20, true);
}

setTimeout(() => {

  movePlaneToRunway(9, 1);
  movePlaneToRunway(12, 2);
  movePlaneToRunway(20, 3);
  movePlaneToRunway(24, 4);
  movePlaneToRunway(25, 5);

  letPlaneHaveEmergency(22);

}, planeSpawnSlideDuration*1000 + 1000);






// ________________________________________________________________________________________________________
// Function Difinitions Section:
// ________________________________________________________________________________________________________

function resizeWindoUpdate() {
  // canvas.width = window.innerWidth;
  // canvas.height = window.innerHeight;

  // container.style.width = (window.innerWidth * 0.9) + 'px';
  // container.style.height = (window.innerHeight/2) + 'px';

}

function createRunways(num) {
  const container = document.getElementById("container");
  // const count = document.getElementById("runwayCount").value;

  // Clear previous runwayes
  container.innerHTML = "";

  for (let i = 0; i < num; i++) {
    const runway = document.createElement("div");
    runway.classList.add("runway");
    runway.id = 'runway:'+String(i + 1);

    runway.style.border = runway_border_thinkness + 'px solid rgba(0, 0, 0, 1)';
    runway.style.width = runway_size + 'px';
    runway.style.height = runway_size + 'px';

    const runwayHat = document.createElement("div");
    runwayHat.classList.add("runway-hat");
    runwayHat.style.width = (runway_size / 2) + 'px';
    runwayHat.style.height = (runway_size / 2) + 'px';;
    


    runway.appendChild(runwayHat);

    container.appendChild(runway);
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

  const anim = plane.animate(
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

  anim.onfinish = () => {
    plane.remove();
  };
}

function updateTimer(numOfMinutes){
  const timer = document.querySelector(".timer");
  // const timer = document.getElementsByName('timer');

  let totalHours = Math.floor(numOfMinutes / 60);

  let totalDays = Math.floor(totalHours / 24);

  numOfMinutes %= 60;

  totalHours %= 24;

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
  plane.style.background = planeEmergencyColor;
}

// Unfinished-----------------------------------------------------------------
function updateInfoScreenContent(planeID){

  const planeInfoScreen = document.querySelector('.display-info-screen');
 

  // get the Aircraft object from the list of Aricrafts??? maybe 

  // const air = getAircraft(planeID);
  // planeInfoScreen.innerHTML = "Aircraft "+planeID+" Info:\
  //     <ul>\
  //       <li>Callsign: "+ air.callsign +"</li>\
  //       <li>Origin: "+ air.origin +"</li>\
  //       <li>Destination: "+ air.destination +"</li>\
  //       <li>Is departure: "+ air.is_departure +"</li>\
  //       <li>Fuel level: "+ air.fuel_level +"</li>\
  //       <li>Emergency status: "+ air.emergency_status +"</li>\
  //       <li>Target time: "+ air.target_time +"</li>\
  //       <li>Actual time: "+ air.actual_time +"</li>\
  //       <li>Current location: "+ air.current_location +"</li>\
  //     </ul> ";

  planeInfoScreen.innerHTML = "Aircraft "+planeID+" Info:\
    <ul>\
      <li>Callsign: "+ 1 +"</li>\
      <li>Origin: "+ 1 +"</li>\
      <li>Destination: "+ 1 +"</li>\
      <li>Is departure: "+ 1 +"</li>\
      <li>Fuel level: "+ 1 +"</li>\
      <li>Emergency status: "+ 1+ "</li>\
      <li>Target time: "+ 1 +"</li>\
      <li>Actual time: "+ 1 +"</li>\
      <li>Current location: "+ 1 +"</li>\
    </ul> ";
}

// Unfinished-----------------------------------------------------------------
// use the plane to return the Aircraft from some global list of current planes in the simulation
function getAircraft(planeID){



}
// ________________________________________________________________________________________________________
// Classes Difinitions Section :
// ________________________________________________________________________________________________________
class Aircraft{
  constructor(ID,c,o,d,i,f,e,t,a,cu){
    this.id = ID;
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
