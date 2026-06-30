window._PUBS = window._PUBS || [];
window._PUBS.push({
  cite: 'arxiv2603_19957',
  doi:  '10.48550/arxiv.2603.19957',
  category: 'preprints',
  thumb: { label: 'arXiv\n2026', bg: 'linear-gradient(135deg,#1c1c1c,#b91c1c)', color: '#fca5a5' },
  title:   'HiPath: Hierarchical Vision-Language Alignment for Structured Pathology Report Prediction',
  titleZh: '/* TODO: 中文标题 */',
  authors: 'R. Yuan, Z. Zhang, <strong>A. Wang</strong>, et al.',
  venue:   '<em>arXiv</em>:2603.19957, 2026.',
  abstract: 'Pathology reports are structured, multi-granular documents encoding diagnostic conclusions, histological grades, and ancillary test results across one or more anatomical sites; yet existing pathology vision-language models (VLMs) reduce this output to a flat label or free-form text. We present HiPath, a lightweight VLM framework built on frozen UNI2 and Qwen3 backbones that treats structured report prediction as its primary training objective. Three trainable modules totalling 15M parameters address complementary aspects of the problem: a Hierarchical Patch Aggregator (HiPA) for multi-image visual encoding, Hierarchical Contrastive Learning (HiCL) for cross-modal alignment via optimal transport, and Slot-based Masked Diagnosis Prediction (Slot-MDP) for structured diagnosis generation. Trained on 749K real-world Chinese pathology cases from three hospitals, HiPath achieves 68.9% strict and 74.7% clinically acceptable accuracy with a 97.3% safety rate, outperforming all baselines under the same frozen backbone. Cross-hospital evaluation confirms generalisation with only a 3.4pp drop in strict accuracy while maintaining 97.1% safety.',
  venueZh: '/* TODO: 中文 venue */',
});
