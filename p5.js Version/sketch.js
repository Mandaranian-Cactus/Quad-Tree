let rects;
let qTree;

function setup() {
  createCanvas(800, 800);
  qTree = new QuadTree(0,0, width, height, 1);
  rects = []
  for (let i = 0; i < 200; i++){
    rects.push(new Rect(random(width - 15), random(height - 15), 15, random(-1.5, 1.5), random(-1.5, 1.5)))
  }
  
  for (let rect of rects){
    qTree.insert(rect); 
  }


  
  // // Debugging
  // line(width/2, 0, width/2, height);
  // line(0, height/2, width, height/2);
  
}

function draw() {
  background(220);
    
  // Clear
  qTree.clear();
  for (let rect of rects){
    rect.state = false;
  }
  
  // Update
  for (let rect of rects){
    rect.update(width, height); 
  }
  
  // Insert
  for (let rect of rects){
    qTree.insert(rect); 
  }
  
//   if (qTree.quads[0] != "empty"){
//     print(qTree.quads[0].objects, qTree.retrieve([], qTree.quads[0].objects[0]))
//   }
  // Do collisions
  for (let rect of rects){
    let pHits = qTree.retrieve([], rect);
    qTree.collisionCheck(pHits, rect);
  }
  
  // Draw rects
  for (let rect of rects){
    rect.render(); 
  }
  
  qTree.drawLines();
  // line(width/2, 0, width/2, height);
  // line(0, height/2, width, height/2);
  
}

function mousePressed(){
  rects.push(new Rect(mouseX, mouseY, 10, 0, 0));
}
