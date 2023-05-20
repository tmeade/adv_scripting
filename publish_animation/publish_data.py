class PublishData():
    '''
    Description: Data object for holding animation publish data
    Arguments:
        asset_name (string): Name of asset
        start_frame (int): start of Animation
        end_frame (int): end of animation
        rig_version (int): version of rig generating the Animation
        publish (bool): Flag in indicate the asset should be publishabled
        cached (bool): Flad to indicate tha asset should be cached
    Returns:
        self.data (dict): object attributes key, value pairs
    '''
    def __init__(
                self,
                asset_name=None,
                start_frame=0,
                end_frame=100,
                rig_version=0,
                publish=False,
                cache=False):
        self.asset_name = asset_name
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.rig_version = rig_version
        self.publish = publish
        self.cache = cache

        self.data = self.__dict__

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return "{}('{}',{},{},{},{},{})".format(
            self.__class__.__name__,
            self.asset_name,
            self.start_frame,
            self.end_frame,
            self.rig_version,
            self.publish,
            self.cache)
