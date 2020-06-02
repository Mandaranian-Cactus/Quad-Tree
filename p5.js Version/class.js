
function overlap(low1, high1, low2, high2){
  if (high1 > high2){
    if (low2 <= low1 && low1 <= high2) return true;
    else return false;
  }
  else if (high2 > high1){
    if (low1 <= low2 && low2 <= high1) return true;
    else return false;
  }
  else return true; // if high2 == high1, they are guarenteed to overlap
}

class Rect{
  constructor(x, y, w, dx, dy){
    this.x = x;
    this.y = y;
    this.w = w;
    this.dx = dx;
    this.dy = dy;
    this.state = false;
  }
  
  update(screenW, screenH){
    let flag = false; // false = no wall collision, true = wall collision
    
    if (this.x < 0){
      this.dx *= - 1;
      this.x = 0;
      flag = true;
    }
    else if (this.x > screenW){
      this.dx *= -1;
      this.x = screenW;
      flag = true;
    }
    
    if (this.y < 0){
      this.dy *= - 1;
      this.y = 0;
      flag = true;
    }
    else if (this.y > screenH){
      this.dy *= - 1;
      this.y = screenH;
      flag = true;
    }
    
    if (!flag){
      this.x += this.dx;
      this.y += this.dy;
    }
    
  }
  
  render(){
    if (this.state) fill(255, 100, 255);
    else fill (50, 50, 50);
    rect(this.x, this.y, this.w, this.w);
  }
}

class QuadTree{
  constructor(x, y, w, h, depth){
    this.x = x;
    this.y = y;
    this.w = w;
    this.h = h;
    this.depth = depth;
    this.maxObjects = 3;
    this.maxDepth = 6;
    this.objects = [];
    this.quads = ["empty", "empty", "empty", "empty"];
  }
  
  clear(){
    this.objects = [];
    if (this.quads[0] != "empty"){
      for (let childTree of this.quads){
        childTree.clear()
        this.quads = ["empty", "empty", "empty", "empty"];
      }
    }
  }
  
  split(){   // Splits a given quadrant into 4 smaller quadrants
    let q1 = new QuadTree(this.x + this.w / 2, this.y, this.w / 2, this.h / 2, this.depth + 1);
    let q2 = new QuadTree(this.x, this.y, this.w / 2, this.h / 2, this.depth + 1);
    let q3 = new QuadTree(this.x, this.y + this.h / 2, this.w / 2, this.h / 2, this.depth + 1);
    let q4 = new QuadTree(this.x + this.w / 2, this.y + this.h / 2, this.w / 2, this.h / 2, this.depth + 1);
    this.quads = [q1, q2, q3, q4];
  }
  
  index(rect){  // Check this out
    let idx = -1;
    let cX = this.x + this.w / 2;
    let cY = this.y + this.h / 2;
    let leftSide = false; let rightSide = false;
        
    // Note that below code assumes that outer border will not be stepped over and that the size of the rectangle is not HUGE 
    if ((rect.x + rect.w) < cX && rect.x > this.x) leftSide = true;
    else if (rect.x > cX && (rect.x + rect.w) < (this.x + this.w)) rightSide = true;
    
    
    if (leftSide){
      if ((rect.y + rect.w) < cY && rect.y > this.y) idx = 1; // 2
      else if (rect.y > cY && (rect.y + rect.w) < (this.y + this.h)) idx = 2; // 3
    }
    else if (rightSide){
      if ((rect.y + rect.w) < cY && rect.y > this.y) idx = 0; // 1
      else if (rect.y > cY && (rect.y + rect.w) < (this.y + this.h)) idx = 3; // 4
    }
    
    return idx;
  }
  
  insert(rect){
    let idx;
    if (this.quads[0] != "empty"){
      idx = this.index(rect);      
      if (idx != -1){
        this.quads[idx].insert(rect);
        return;
      }
    }
    
    // Here, we are either at a leaf node or have gotten an overlap case
    this.objects.push(rect);
    if (this.objects.length > this.maxObjects && this.depth < this.maxDepth && idx != -1){
      this.split();
      for (let i = this.objects.length - 1; i >= 0; i--){
        let object = this.objects[i];
        let idx = this.index(object);
        if (idx != -1){
          this.objects.splice(i, 1);
          this.quads[idx].insert(object);  // This line can probably be simplified since we are 
        }
      }
    }
  }
  
  retrieve(pHits, rect){ // Retrieve function error?
    
    // Going down
    let idx = this.index(rect);
    if (this.quads[0] != "empty" && idx != -1){
        pHits = this.quads[idx].retrieve(pHits, rect);
      }

    pHits = concat(pHits, this.objects);
    return pHits;
  }
  
  collisionCheck(pHits, rect){
    let hits = [];
    for (let object of pHits){
      if (object != rect){
        if (overlap(rect.x, rect.x + rect.w, object.x, object.x + object.w)){
          if (overlap(rect.y, rect.y + rect.w, object.y, object.y + object.w)) hits.push(object);
        }
      }
    }
    
    if (hits.length > 0) rect.state = true;
    for (let hit of hits){
      hit.state = true;
    }    
  }
  
  drawLines(){
    if (this.quads[0] != "empty"){
      fill(0,0,0);
      line(this.x + this.w / 2, this.y, this.x + this.w / 2, this.y + this.h);  // Vert Line
      line(this.x, this.y + this.h / 2, this.x + this.w, this.y + this.h / 2);
      for (let cQuad of this.quads){
        cQuad.drawLines() 
      }
    }
  }
}

 
