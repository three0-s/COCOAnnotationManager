from copy import copy
import random

class COCOAnnotationManager:
    TOTAL_IMAGE_NUM=0
    TOTAL_ANNON_NUM=0
    
    def __init__(self, annotation_dict):
        self.image_num = len(annotation_dict['images'])
        self.annon_num = len(annotation_dict['annotations'])
        self.annon_dict = copy(annotation_dict)
        
        # img id pair = {new img id: preveious img id}
        self.img_id_pair = {}
        for i, img_dict in enumerate(annotation_dict['images']):
            self.img_id_pair[img_dict['id']]=i+COCOAnnotationManager.TOTAL_IMAGE_NUM 
        COCOAnnotationManager.TOTAL_IMAGE_NUM += self.image_num
        
        img_dict_list = []
        for img_dict in annotation_dict['images']:
            copy_dict = copy(img_dict)
            del copy_dict['path']
            copy_dict['id'] = self.img_id_pair[img_dict['id']]
            img_dict_list.append(copy(copy_dict))
        
        self.annon_dict.update(images=img_dict_list)
        
        # img annon pair = {new annon id: preveious annon id}
        self.annon_id_pair = {}
        for i, annon_dict in enumerate(annotation_dict['annotations']):
            self.annon_id_pair[annon_dict['id']]=i+COCOAnnotationManager.TOTAL_ANNON_NUM
        COCOAnnotationManager.TOTAL_ANNON_NUM += self.annon_num
        
        annotations_list = []
        for annon_dict in annotation_dict['annotations']:
            copy_dict = copy(annon_dict)
            copy_dict['id'] = self.annon_id_pair[annon_dict['id']]
            copy_dict['image_id'] = self.img_id_pair[annon_dict['image_id']]
            annotations_list.append(copy(copy_dict))
            
        self.annon_dict.update(annotations=annotations_list)

    def merge(self, *annon_dicts)->dict:
        merged_dict = {}
        images_list = copy(self.annon_dict['images'])
        annons_list = copy(self.annon_dict['annotations'])

        for annon_dict in annon_dicts:
            images_list.extend(copy(annon_dict['images']))
            annons_list.extend(copy(annon_dict['annotations']))
            self.image_num += len(annon_dict['images'])
            self.annon_num += len(annon_dict['annotations'])

        merged_dict['images']=images_list
        merged_dict['annotations']=annons_list
        # assume all annon dicts have same category
        merged_dict['categories']=copy(self.annon_dict['categories'])

        assert self.image_num == len(merged_dict['images']) and self.annon_num == len(merged_dict['annotations']), "LENGTH ASSERTION ERROR IN MERGE!"
        return merged_dict
    
    def split(self, n, *ratios)->list:
        assert n == len(ratios), "A list of ratio of splits should have length of n"
        splits_list = [{'categories':copy(self.annon_dict['categories'])} for i in range(n)]

        length_list = [int(self.image_num * ratio) for i, ratio in enumerate(ratios) if i != n-1]
        length_list.append(self.image_num-sum(length_list))

        imgId_annonDict_pair = {}
        for annon_dict in self.annon_dict['annotations']:
            if annon_dict['image_id'] in imgId_annonDict_pair.keys():
                imgId_annonDict_pair[annon_dict['image_id']].append(copy(annon_dict))
            else:
                imgId_annonDict_pair[annon_dict['image_id']] = [copy(annon_dict)]

        split_indices = list(range(self.image_num))
        random.shuffle(split_indices)
        prev=0
        for i, length in enumerate(length_list):
            indices = split_indices[prev:length]
            splits_list[i]['images'] = [copy(self.annon_dict['images'][idx]) for idx in indices]

            annons_list = []
            for img_dict in splits_list[i]['images']:
                annons_list.extend(copy(imgId_annonDict_pair[img_dict['id']]))
            splits_list[i]['annotations'] = copy(annons_list)
            prev+=length
        
        return splits_list
       
