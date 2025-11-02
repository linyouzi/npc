// 3D NPC 顯示和互動邏輯
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

let scene, camera, renderer, npcModel, mixer, clock;
let isAnimating = false;

// 初始化 3D 場景
function init3DScene() {
    const container = document.getElementById('canvas-container');
    const canvas = document.getElementById('npc-canvas');
    
    // 創建場景
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1e3c72);
    
    // 創建相機
    camera = new THREE.PerspectiveCamera(
        75,
        container.clientWidth / container.clientHeight,
        0.1,
        1000
    );
    camera.position.set(0, 1.5, 3);
    camera.lookAt(0, 1, 0);
    
    // 創建渲染器
    renderer = new THREE.WebGLRenderer({
        canvas: canvas,
        antialias: true
    });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.shadowMap.enabled = true;
    
    // 添加光源
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 10, 5);
    directionalLight.castShadow = true;
    scene.add(directionalLight);
    
    // 添加地面
    const groundGeometry = new THREE.PlaneGeometry(10, 10);
    const groundMaterial = new THREE.MeshStandardMaterial({ color: 0x444444 });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);
    
    clock = new THREE.Clock();
    
    // 載入 NPC 模型
    loadNPCModel();
    
    // 處理視窗大小改變
    window.addEventListener('resize', onWindowResize);
}

// 載入 NPC 3D 模型
function loadNPCModel() {
    const loader = new THREE.GLTFLoader();
    
    // 如果從 Omniverse 導出的模型路徑
    // 預設使用一個簡單的幾何體作為示範
    // 實際使用時，將 'models/npc.glb' 替換為你從 Omniverse 導出的模型路徑
    
    try {
        // 嘗試載入外部模型（如果存在）
        loader.load(
            'models/npc.glb',
            (gltf) => {
                npcModel = gltf.scene;
                npcModel.position.set(0, 0, 0);
                npcModel.scale.set(1, 1, 1);
                scene.add(npcModel);
                
                // 如果有動畫
                if (gltf.animations && gltf.animations.length > 0) {
                    mixer = new THREE.AnimationMixer(npcModel);
                    gltf.animations.forEach((clip) => {
                        mixer.clipAction(clip).play();
                    });
                    isAnimating = true;
                }
                
                document.getElementById('loading').style.display = 'none';
                document.getElementById('npc-status').textContent = '已載入';
                animate();
            },
            (progress) => {
                const percent = (progress.loaded / progress.total) * 100;
                document.getElementById('loading').textContent = `載入中... ${percent.toFixed(0)}%`;
            },
            (error) => {
                console.error('載入模型失敗，使用預設模型:', error);
                createDefaultNPC();
            }
        );
    } catch (error) {
        console.error('載入模型錯誤:', error);
        createDefaultNPC();
    }
}

// 創建預設 NPC（當沒有外部模型時）
function createDefaultNPC() {
    // 創建一個簡單的 NPC 角色作為示範
    const group = new THREE.Group();
    
    // 身體
    const bodyGeometry = new THREE.CylinderGeometry(0.4, 0.4, 1.2, 8);
    const bodyMaterial = new THREE.MeshStandardMaterial({ color: 0x4a90e2 });
    const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
    body.position.y = 1.1;
    body.castShadow = true;
    group.add(body);
    
    // 頭部
    const headGeometry = new THREE.SphereGeometry(0.35, 16, 16);
    const headMaterial = new THREE.MeshStandardMaterial({ color: 0xffdbac });
    const head = new THREE.Mesh(headGeometry, headMaterial);
    head.position.y = 2.1;
    head.castShadow = true;
    group.add(head);
    
    // 眼睛
    const eyeGeometry = new THREE.SphereGeometry(0.05, 8, 8);
    const eyeMaterial = new THREE.MeshStandardMaterial({ color: 0x000000 });
    
    const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
    leftEye.position.set(-0.1, 2.15, 0.3);
    group.add(leftEye);
    
    const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
    rightEye.position.set(0.1, 2.15, 0.3);
    group.add(rightEye);
    
    // 手臂
    const armGeometry = new THREE.CylinderGeometry(0.1, 0.1, 0.8, 8);
    const armMaterial = new THREE.MeshStandardMaterial({ color: 0xffdbac });
    
    const leftArm = new THREE.Mesh(armGeometry, armMaterial);
    leftArm.position.set(-0.6, 1.2, 0);
    leftArm.rotation.z = Math.PI / 6;
    leftArm.castShadow = true;
    group.add(leftArm);
    
    const rightArm = new THREE.Mesh(armGeometry, armMaterial);
    rightArm.position.set(0.6, 1.2, 0);
    rightArm.rotation.z = -Math.PI / 6;
    rightArm.castShadow = true;
    group.add(rightArm);
    
    // 腿部
    const legGeometry = new THREE.CylinderGeometry(0.12, 0.12, 0.8, 8);
    const legMaterial = new THREE.MeshStandardMaterial({ color: 0x2c3e50 });
    
    const leftLeg = new THREE.Mesh(legGeometry, legMaterial);
    leftLeg.position.set(-0.2, 0.4, 0);
    leftLeg.castShadow = true;
    group.add(leftLeg);
    
    const rightLeg = new THREE.Mesh(legGeometry, legMaterial);
    rightLeg.position.set(0.2, 0.4, 0);
    rightLeg.castShadow = true;
    group.add(rightLeg);
    
    npcModel = group;
    scene.add(npcModel);
    
    document.getElementById('loading').style.display = 'none';
    document.getElementById('npc-status').textContent = '已載入（預設模型）';
    animate();
}

// 動畫循環
function animate() {
    requestAnimationFrame(animate);
    
    if (mixer && isAnimating) {
        mixer.update(clock.getDelta());
    }
    
    renderer.render(scene, camera);
}

// 視窗大小改變處理
function onWindowResize() {
    const container = document.getElementById('canvas-container');
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
}

// 控制函數（需要在全局作用域）
window.rotateNPC = function() {
    if (npcModel) {
        npcModel.rotation.y += Math.PI / 2;
    }
}

window.resetView = function() {
    if (camera) {
        camera.position.set(0, 1.5, 3);
        camera.lookAt(0, 1, 0);
    }
    if (npcModel) {
        npcModel.rotation.y = 0;
    }
}

window.toggleAnimation = function() {
    if (mixer) {
        isAnimating = !isAnimating;
        const status = isAnimating ? '播放中' : '已暫停';
        document.getElementById('npc-status').textContent = status;
    } else {
        alert('當前模型沒有動畫');
    }
}

window.changeEmotion = function(emotion) {
    document.getElementById('npc-emotion').textContent = emotion;
    
    // 這裡可以根據情緒改變模型顏色或姿勢
    if (npcModel && npcModel.children) {
        const emotionColors = {
            happy: 0xffd700,
            sad: 0x4169e1,
            neutral: 0x4a90e2
        };
        
        // 改變身體顏色
        npcModel.children.forEach(child => {
            if (child.material && child.material.color) {
                // 只改變身體部分
                if (child.geometry && child.geometry.type === 'CylinderGeometry') {
                    child.material.color.setHex(emotionColors[emotion] || 0x4a90e2);
                }
            }
        });
    }
}

// 初始化
window.addEventListener('DOMContentLoaded', () => {
    init3DScene();
});

