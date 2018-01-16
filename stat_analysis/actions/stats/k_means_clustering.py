import logging
import random
import matplotlib.pyplot as plt
import numpy as np
from kivy.app import App
from stat_analysis.actions.base_action import BaseAction
from stat_analysis.generic_widgets.bordered import BorderedTable
from stat_analysis.generic_widgets.form_outputs import ExportableGraph

logger = logging.getLogger(__name__)

class KMeansClustering(BaseAction):
    type = "stats.k_means_clustering"
    view_name  = "K Means Clustering"

    def __init__(self,output_widget):
        self.save_name = ""
        self.status = "OK"
        self.form = [
            {
                "group_name": "Data",
                "inputs": [
                    {
                        "input_type": "combo_box",
                        "data_type": "dataset",
                        "required": True,
                        "form_name": "dataset",
                        "visible_name": "Data Set",
                        "on_change": lambda x, val: x.parent_action.set_tmp_dataset(val)
                    },
                    {
                        "input_type": "combo_box",
                        "data_type": "column_numeric",
                        "get_cols_from": lambda x: x.parent_action.tmp_dataset,
                        "add_dataset_listener": lambda x: x.parent_action.add_dataset_listener(x),
                        "required": True,
                        "form_name": "x_var",
                        "visible_name": "X Variable"
                    },
                    {
                        "input_type": "combo_box",
                        "data_type": "column",
                        "get_cols_from": lambda x: x.parent_action.tmp_dataset,
                        "add_dataset_listener": lambda x: x.parent_action.add_dataset_listener(x),
                        "required": True,
                        "form_name": "y_var",
                        "visible_name": "Y Variable"
                    }
                ]
            },
            {
                "group_name":"Model Options",
                "inputs":[
                    {
                        "input_type": "numeric",
                        "required": True,
                        "form_name": "k",
                        "visible_name": "K",
                        "tip": "Number of clusters"
                    },
                    {
                        "input_type":"check_box",
                        "required":True,
                        "form_name":"init_rnd_num",
                        "visible_name":"Initialise with a random point",
                        "tip":"The centroids will either be initialised with a random point from the dataset"
                              " or a random point in the data's range. Initialising with a random point can"
                              " cause centroids to not be used"
                    }
                ]
            },
            {
                "group_name": "Save",
                "inputs": [
                    {
                        "input_type": "check_box",
                        "required": True,
                        "form_name": "save_action",
                        "visible_name": "Save action"
                    },
                    {
                        "input_type": "string",
                        "required": True,
                        "visible_name": "Action save name",
                        "form_name": "action_save_name"
                    }
                ]
            }
        ]
        self.output_widget = output_widget
        self.tmp_dataset = None
        self.tmp_dataset_listeners = []
        self.stored_model = None

    def set_tmp_dataset(self, val):
        self.tmp_dataset = val
        [form_item.try_populate(quiet=True) for form_item in self.tmp_dataset_listeners]

    def add_dataset_listener(self, val):
        self.tmp_dataset_listeners.append(val)

    def run(self,validate=True,quiet=False,preloaded=False,use_cached=False,**kwargs):
        logger.info("Running action {}".format(self.type))
        if validate:
            if not self.validate_form():
                logger.warning("Form not validated, form errors: {}".format(self.form_errors))
                return False
            else:
                logger.debug("Form validated, form outputs: {}".format(self.form_outputs))

        vals = self.form_outputs
        dataset = App.get_running_app().get_dataset_by_name(vals["dataset"])

        if dataset == False:
            # Dataset not found
            return False

        x_pos = list(dataset.get_header_structure().keys()).index(vals["x_var"])
        y_pos = list(dataset.get_header_structure().keys()).index(vals["y_var"])
        x,y = [],[]

        for row in dataset.get_data():
            x.append(row[x_pos])
            y.append(row[y_pos])

        model = KMeans(k=int(vals["k"]),init_rnd_point=vals["init_rnd_num"])
        model.fit(x,y)

        cols = ["r","g","b","c","k"]
        if not quiet:
            fig = plt.figure()
            axis = plt.subplot(111)
            cols = cols*int(vals["k"])
            for i,group in enumerate(model.classes):
                group_x = []
                group_y = []
                for point in group:
                    group_x.append(point[0])
                    group_y.append(point[1])

                plt.scatter(group_x,group_y,color=cols[i])
                plt.scatter(model.centroids[i][0],model.centroids[i][1],marker="x",color=cols[i])

            axis.legend()
            fig.savefig("tmp/plot.png")
            self.result_output.clear_outputs()
            self.result_output.add_widget(ExportableGraph(source="tmp/plot.png", fig=fig, axis=[axis], nocache=True,
                                                          size_hint_y=None))


class KMeans(object):
    def __init__(self, k=3, tolerance=0.0001, max_iterations=500, init_rnd_point=False):
        self.k = k
        self.tolerance = tolerance
        self.max_iterations = max_iterations
        self.centroids = []
        self.init_rnd_point = init_rnd_point
        self.is_optimal = False

    def fit(self, x, y):
        min_x = min(x)
        max_x = max(x)
        min_y = min(y)
        max_y = max(y)

        # Initialise the centeroids
        self.centroids = [None] * self.k
        for i in range(self.k):
            if self.init_rnd_point:
                self.centroids[i] = [random.random() * (max_x - min_x) + min_x,
                                     random.random() * (max_y - min_y) + min_y]
            else:
                pos = random.randrange(0,len(x))
                self.centroids[i] = [x[pos],y[pos]]

        # Main loop for fitting centroids
        for i in range(self.max_iterations):
            self.classes = []
            [self.classes.append([]) for x in range(self.k)]

            for data_pos in range(len(x)):
                distances = [self.euclidean_dist([x[data_pos], y[data_pos]], centroid) for centroid in self.centroids]
                # Get the smallest distance to a centroid, and add that to the centroid
                opt_centroid = distances.index(min(distances))
                self.classes[opt_centroid].append([x[data_pos], y[data_pos]])

            prev = self.centroids[:]

            # Average the cluster data points to get a new centroid
            for j, classification in enumerate(self.classes):
                if len(classification) != 0:
                    ave_x = sum([_x[0] for _x in classification]) / len(classification)
                    ave_y = sum([_y[1] for _y in classification]) / len(classification)
                    self.centroids[j] = [ave_x, ave_y]

            self.is_optimal = True

            # Check if all centroids have converged (within self.tolerance)
            for centroid_pos in range(0,len(self.centroids)):
                original = prev[centroid_pos]
                curr = self.centroids[centroid_pos]

                sum_delta = 0
                # Sum up percentage changes for each axis

                for axis in range(0,len(original)):
                    try:
                        sum_delta += abs((curr[axis] - original[axis])/original[axis] * 100)
                    except ZeroDivisionError:
                        pass

                if sum_delta > self.tolerance:
                    # Fit hasn't converged
                    self.is_optimal = False

            if self.is_optimal:
                return True


    @staticmethod
    def euclidean_dist(p1, p2):
        squared_dist = 0

        for i in range(0, len(p1)):
            squared_dist += (p1[i] - p2[i]) ** 2

        return squared_dist ** 0.5

