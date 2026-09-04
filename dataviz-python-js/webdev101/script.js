'use strict';

/**
 * script.js — the JavaScript half of the webdev101 demo page.
 *
 * Split into three independent parts, matching the three sections of
 * the page after the intro:
 *   1. Populating the Pokemon list from a plain data array (DOM text).
 *   2. A 2D canvas animation: bouncing geometric shapes.
 *   3. A pseudo-3D canvas animation: a rotating wireframe cube.
 *
 * Per docs/javascript.md, jQuery ($) is used for DOM selection/mutation
 * and event binding; the canvas drawing itself uses the native Canvas
 * API, since jQuery has no opinion about pixel drawing.
 */

// Wait for the DOM to be ready before touching any elements — jQuery's
// $(...) shorthand for document.ready(), same idea as vanilla JS's
// 'DOMContentLoaded' event.
$(function () {
  renderPokemonList();
  setupCanvas2dDemo();
  setupCanvas3dDemo();
});

// ============================================================
// SECTION 1 — Populate the Pokemon list from data
// ============================================================

/** Small, self-contained sample dataset — just enough to demonstrate
 * "data drives markup" rather than hand-typing each <li> in index.html. */
const POKEMON_DATA = [
  { name: 'Bulbasaur', type: 'grass', description: 'A seed Pokemon that basks in sunlight to grow.' },
  { name: 'Charmander', type: 'fire', description: 'The flame on its tail shows its life force.' },
  { name: 'Squirtle', type: 'water', description: 'Withdraws into its shell to protect itself.' },
  { name: 'Pikachu', type: 'electric', description: 'Stores electricity in its cheek pouches.' },
];

/** Background color per Pokemon type, used for the small badge on each card. */
const TYPE_COLORS = {
  grass: '#4caf50',
  fire: '#ff7043',
  water: '#42a5f5',
  electric: '#fdd835',
};

/**
 * Builds one <li class="pokemon-card"> per entry in POKEMON_DATA and
 * appends them to #pokemon-list. Demonstrates the common pattern of
 * keeping content data (POKEMON_DATA) separate from markup (index.html),
 * with JS as the glue that renders one into the other.
 */
function renderPokemonList() {
  const $list = $('#pokemon-list');

  POKEMON_DATA.forEach(function (pokemon) {
    const badgeColor = TYPE_COLORS[pokemon.type] || '#999';

    // Building the card as a jQuery object lets us use .css()/.text()
    // instead of hand-assembling an HTML string, which avoids any risk
    // of accidentally injecting unescaped text as markup.
    const $card = $('<li class="pokemon-card"></li>');
    $('<h3></h3>').text(pokemon.name).appendTo($card);
    $('<p></p>').text(pokemon.description).appendTo($card);
    $('<span class="type-badge"></span>')
      .text(pokemon.type)
      .css('background-color', badgeColor)
      .appendTo($card);

    $list.append($card);
  });
}

// ============================================================
// SECTION 2 — 2D canvas: bouncing geometric shapes
// ============================================================

/**
 * Wires up the #canvas-2d demo: a few shapes bounce around inside the
 * canvas bounds, redrawn every animation frame. Also wires the
 * pause/resume and reset buttons.
 */
function setupCanvas2dDemo() {
  const canvas = document.getElementById('canvas-2d');
  const ctx = canvas.getContext('2d');

  // Each shape tracks its own position (x, y), velocity (vx, vy) in
  // pixels/frame, a size, a color, and which drawing routine to use.
  function createInitialShapes() {
    return [
      { kind: 'circle', x: 60, y: 60, vx: 2.2, vy: 1.6, size: 24, color: TYPE_COLORS.fire },
      { kind: 'square', x: 200, y: 120, vx: -1.8, vy: 2.4, size: 36, color: TYPE_COLORS.water },
      { kind: 'triangle', x: 340, y: 80, vx: 1.5, vy: -2.0, size: 32, color: TYPE_COLORS.grass },
      { kind: 'circle', x: 400, y: 220, vx: -2.4, vy: -1.4, size: 18, color: TYPE_COLORS.electric },
    ];
  }

  let shapes = createInitialShapes();
  let animationFrameId = null;
  let running = true;

  /** Draws a single shape at its current (x, y) according to its kind. */
  function drawShape(shape) {
    ctx.fillStyle = shape.color;

    if (shape.kind === 'circle') {
      ctx.beginPath();
      ctx.arc(shape.x, shape.y, shape.size / 2, 0, Math.PI * 2);
      ctx.fill();
    } else if (shape.kind === 'square') {
      ctx.fillRect(shape.x - shape.size / 2, shape.y - shape.size / 2, shape.size, shape.size);
    } else if (shape.kind === 'triangle') {
      const half = shape.size / 2;
      ctx.beginPath();
      ctx.moveTo(shape.x, shape.y - half);
      ctx.lineTo(shape.x - half, shape.y + half);
      ctx.lineTo(shape.x + half, shape.y + half);
      ctx.closePath();
      ctx.fill();
    }
  }

  /** Moves a shape by its velocity and bounces it off the canvas walls. */
  function updateShape(shape) {
    shape.x += shape.vx;
    shape.y += shape.vy;

    const half = shape.size / 2;

    // Flip the relevant velocity component whenever the shape's edge
    // would cross a wall — this is a simple bounce, not real physics
    // (no energy loss, no rotation), which is intentional for clarity.
    if (shape.x - half < 0 || shape.x + half > canvas.width) {
      shape.vx *= -1;
    }
    if (shape.y - half < 0 || shape.y + half > canvas.height) {
      shape.vy *= -1;
    }
  }

  /** One full animation frame: clear, update every shape, redraw every shape. */
  function tick() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    shapes.forEach(function (shape) {
      updateShape(shape);
      drawShape(shape);
    });

    if (running) {
      animationFrameId = requestAnimationFrame(tick);
    }
  }

  // Kick off the animation loop immediately on page load.
  animationFrameId = requestAnimationFrame(tick);

  // Pause/resume: cancelAnimationFrame stops the loop from scheduling
  // its next frame; toggling `running` back on restarts it.
  $('#btn-2d-toggle').on('click', function () {
    running = !running;
    $(this).text(running ? 'Pause' : 'Resume');

    if (running) {
      animationFrameId = requestAnimationFrame(tick);
    } else {
      cancelAnimationFrame(animationFrameId);
    }
  });

  // Reset: put the shapes back to their starting positions/velocities
  // without touching whether the animation is currently running.
  $('#btn-2d-reset').on('click', function () {
    shapes = createInitialShapes();
  });
}

// ============================================================
// SECTION 3 — Pseudo-3D canvas: rotating wireframe cube
// ============================================================

/**
 * Wires up the #canvas-3d demo: a cube described by 8 corner points in
 * 3D space is rotated every frame and projected down onto the flat 2D
 * canvas, then drawn as connected line segments ("wireframe").
 */
function setupCanvas3dDemo() {
  const canvas = document.getElementById('canvas-3d');
  const ctx = canvas.getContext('2d');
  const centerX = canvas.width / 2;
  const centerY = canvas.height / 2;

  // The 8 corners of a cube centered on the origin, side length 160
  // (so each coordinate is +/-80). Using (x, y, z) triples is what
  // makes this "3D" — a plain 2D canvas has no idea what a z-axis is,
  // we just do the geometry ourselves before drawing.
  const CUBE_SIZE = 80;
  const vertices = [
    [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
    [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1],
  ].map(function ([x, y, z]) {
    return [x * CUBE_SIZE, y * CUBE_SIZE, z * CUBE_SIZE];
  });

  // Which vertex indices are connected by an edge — 12 edges total
  // (4 on the front face, 4 on the back face, 4 connecting them).
  const EDGES = [
    [0, 1], [1, 2], [2, 3], [3, 0], // front face
    [4, 5], [5, 6], [6, 7], [7, 4], // back face
    [0, 4], [1, 5], [2, 6], [3, 7], // connectors
  ];

  /**
   * Rotates a 3D point around the X and Y axes by the given angles
   * (radians), using the standard rotation matrices. Rotating around
   * two axes at once (rather than just one) is what makes the cube's
   * motion look properly three-dimensional instead of a flat spin.
   */
  function rotatePoint([x, y, z], angleX, angleY) {
    // Rotate around the X axis: Y and Z mix, X stays fixed.
    const cosX = Math.cos(angleX);
    const sinX = Math.sin(angleX);
    const y1 = y * cosX - z * sinX;
    const z1 = y * sinX + z * cosX;

    // Rotate around the Y axis: X and Z mix, Y stays fixed.
    const cosY = Math.cos(angleY);
    const sinY = Math.sin(angleY);
    const x2 = x * cosY + z1 * sinY;
    const z2 = -x * sinY + z1 * cosY;

    return [x2, y1, z2];
  }

  /**
   * Projects a rotated 3D point onto 2D canvas coordinates using a
   * simple perspective projection: points further away (larger z)
   * are scaled down, which is what gives the cube a sense of depth.
   */
  function project([x, y, z]) {
    const cameraDistance = 400;
    const scale = cameraDistance / (cameraDistance + z);
    return [centerX + x * scale, centerY + y * scale];
  }

  let angleX = 0.4; // fixed base tilt so we see more than one face
  let angleY = 0;
  let running = true;
  let animationFrameId = null;

  function tick() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Rotate + project every vertex once per frame, then draw a line
    // for each edge between the resulting 2D points.
    const projected = vertices.map(function (vertex) {
      return project(rotatePoint(vertex, angleX, angleY));
    });

    ctx.strokeStyle = TYPE_COLORS.electric;
    ctx.lineWidth = 2;

    EDGES.forEach(function ([startIndex, endIndex]) {
      const [x1, y1] = projected[startIndex];
      const [x2, y2] = projected[endIndex];
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();
    });

    // Only spinning around Y (left-right) each frame keeps the motion
    // easy to follow; angleX stays fixed at its initial tilt.
    angleY += 0.015;

    if (running) {
      animationFrameId = requestAnimationFrame(tick);
    }
  }

  animationFrameId = requestAnimationFrame(tick);

  $('#btn-3d-toggle').on('click', function () {
    running = !running;
    $(this).text(running ? 'Pause' : 'Resume');

    if (running) {
      animationFrameId = requestAnimationFrame(tick);
    } else {
      cancelAnimationFrame(animationFrameId);
    }
  });
}
