window._PUBS = window._PUBS || [];
window._PUBS.push({
  cite: 'zhang2024constraint',
  doi:  '10.1109/tmi.2024.3412935',
  category: 'published',
  thumb: { label: 'IEEE\nTMI\n2024', bg: 'linear-gradient(135deg,#7c2d12,#9a3412)', color: '#fca5a5' },
  title:   'Constraint-Aware Learning for Fractional Flow Reserve Pullback Curve Estimation From Invasive Coronary Imaging',
  titleZh: '基于约束感知学习的有创冠脉影像 FFR 回拉曲线估算。',
  authors: 'D. Zhang, X. Liu, <strong>A. Wang</strong>, et al.',
  venue:   '<em>IEEE Transactions on Medical Imaging</em>, 43(12): 4091-4104, 2024.',
  abstract: 'Estimation of the fractional flow reserve (FFR) pullback curve from invasive coronary imaging is important for the intraoperative guidance of coronary intervention. Machine/deep learning has been proven effective in FFR pullback curve estimation. However, the existing methods suffer from inadequate incorporation of intrinsic geometry associations and physics knowledge. In this paper, we propose a constraint-aware learning framework to improve the estimation of the FFR pullback curve from invasive coronary imaging. It incorporates both geometrical and physical constraints to approximate the relationships between the geometric structure and FFR values along the coronary artery centerline. Our method also leverages the power of synthetic data in model training to reduce the collection costs of clinical data. Moreover, to bridge the domain gap between synthetic and real data distributions when testing on real-world imaging data, we also employ a diffusion-driven test-time data adaptation method that preserves the knowledge learned in synthetic data. Specifically, this method learns a diffusion model of the synthetic data distribution and then projects real data to the synthetic data distribution at test time. Extensive experimental studies on a synthetic dataset and a real-world dataset of 382 patients covering three imaging modalities have shown the better performance of our method for FFR estimation of stenotic coronary arteries, compared with other machine/deep learning-based FFR estimation models and computational fluid dynamics-based model. The results also provide high agreement and correlation between the FFR predictions of our method and the invasively measured FFR values. The plausibility of FFR predictions along the coronary artery centerline is also validated.',
  venueZh: '<em>IEEE Transactions on Medical Imaging</em>，43(12): 4091–4104，2024。',
  badge: 'SCI Q1 Top · IF 8.1', badgeClass: 'top',
});
