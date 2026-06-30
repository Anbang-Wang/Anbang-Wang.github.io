window._PUBS = window._PUBS || [];
window._PUBS.push({
  cite: 'arxiv2603_11325',
  doi:  '10.48550/arxiv.2603.11325',
  category: 'preprints',
  thumb: { label: 'arXiv\n2026', bg: 'linear-gradient(135deg,#1c1c1c,#b91c1c)', color: '#fca5a5' },
  title:   'Towards Trustworthy Selective Generation: Reliability-Guided Diffusion for Ultra-Low-Field to High-Field MRI Synthesis',
  titleZh: '/* TODO: 中文标题 */',
  authors: 'Z. Zhang, P. Jing, <strong>A. Wang</strong>, et al.',
  venue:   '<em>arXiv</em>:2603.11325, 2026.',
  abstract: 'Low-field to high-field MRI synthesis has emerged as a cost-effective strategy to enhance image quality under hardware and acquisition constraints, particularly in scenarios where access to high-field scanners is limited or impractical. Despite recent progress in diffusion models, diffusion-based approaches often struggle to balance fine-detail recovery and structural fidelity. In particular, the uncontrolled generation of high-resolution details in structurally ambiguous regions may introduce anatomically inconsistent patterns, such as spurious edges or artificial texture variations. These artifacts can bias downstream quantitative analysis. For example, they may cause inaccurate tissue boundary delineation or erroneous volumetric estimation, ultimately reducing clinical trust in synthesized images. These limitations highlight the need for generative models that are not only visually accurate but also spatially reliable and anatomically consistent. To address this issue, we propose a reliability-aware diffusion framework (ReDiff) that improves synthesis robustness at both the sampling and post-generation stages. Specifically, we introduce a reliability-guided sampling strategy to suppress unreliable responses during the denoising process. We further develop an uncertainty-aware multi-candidate selection scheme to enhance the reliability of the final prediction. Experiments on multi-center MRI datasets demonstrate improved structural fidelity and reduced artifacts compared with state-of-the-art methods.',
  venueZh: '/* TODO: 中文 venue */',
});
