from kiali_qe.entities import EntityBase


class Workload(EntityBase):

    def __init__(self, name, namespace, workload_type,
                 istio_sidecar=None, app_label=None, version_label=None):
        self.name = name
        self.namespace = namespace
        self.workload_type = workload_type
        self.istio_sidecar = istio_sidecar
        self.app_label = app_label
        self.version_label = version_label

    def __str__(self):
        return 'name:{}, namespace:{}, type:{}, sidecar:{}, app:{}, version:{}'.format(
            self.name, self.namespace, self.workload_type,
            self.istio_sidecar, self.app_label, self.version_label)

    def __repr__(self):
        return "{}({}, {}, {}, {}, {}, {})".format(
            type(self).__name__, repr(self.name), repr(self.namespace), repr(self.workload_type),
            repr(self.istio_sidecar), repr(self.app_label), repr(self.version_label))

    def __eq__(self, other):
        return self.is_equal(other, advanced_check=True)

    def is_equal(self, other, advanced_check=True):
        # basic check
        if not isinstance(other, Workload):
            return False
        if self.name != other.name:
            return False
        if self.namespace != other.namespace:
            return False
        if self.workload_type != other.workload_type:
            return False
        # advanced check
        if advanced_check:
            if self.istio_sidecar != other.istio_sidecar:
                return False
            if self.app_label != other.app_label:
                return False
            if self.version_label != other.version_label:
                return False
        return True


class WorkloadDetails(EntityBase):

    def __init__(self, name, workload_type, created_at, resource_version,
                 istio_sidecar=False, **kwargs):
        if name is None:
            raise KeyError("'name' should not be 'None'")
        self.name = name
        self.workload_type = workload_type
        self.istio_sidecar = istio_sidecar
        self.created_at = created_at
        self.resource_version = resource_version
        self.replicas = kwargs['replicas']\
            if 'replicas' in kwargs else None
        self.availableReplicas = kwargs['availableReplicas']\
            if 'availableReplicas' in kwargs else None
        self.unavailableReplicas = kwargs['unavailableReplicas']\
            if 'unavailableReplicas' in kwargs else None
        self.workload_type = kwargs['workload_type']\
            if 'workload_type' in kwargs else None
        self.created_at = kwargs['created_at']\
            if 'created_at' in kwargs else None
        self.resource_version = kwargs['resource_version']\
            if 'resource_version' in kwargs else None
        self.pods_number = kwargs['pods_number']\
            if 'pods_number' in kwargs else None
        self.services_number = kwargs['services_number']\
            if 'services_number' in kwargs else None
        self.services = kwargs['services']\
            if 'services' in kwargs else None
        self.pods = kwargs['pods']\
            if 'pods' in kwargs else None

    def __str__(self):
        return 'name:{}, type:{}, sidecar:{}, createdAt:{}, resourceVersion:{}'.format(
            self.name, self.workload_type,
            self.istio_sidecar, self.created_at, self.resource_version)

    def __repr__(self):
        return "{}({}, {}, {}, {}, {})".format(
            type(self).__name__, repr(self.name), repr(self.workload_type),
            repr(self.istio_sidecar), repr(self.created_at),
            repr(self.resource_version))

    def __eq__(self, other):
        return self.is_equal(other, advanced_check=True)

    def is_equal(self, other, advanced_check=True):
        # basic check
        if not isinstance(other, WorkloadDetails):
            return False
        if self.name != other.name:
            return False
        if self.workload_type != other.workload_type:
            return False
        if self.created_at != other.created_at:
            return False
        if self.resource_version != other.resource_version:
            return False
        # advanced check
        if advanced_check:
            if self.istio_sidecar != other.istio_sidecar:
                return False
        return True


class WorkloadPod(EntityBase):

    def __init__(self, name, created_at, created_by,
                 istio_init_containers=None, istio_containers=None):
        self.name = name
        self.created_at = created_at
        self.created_by = created_by
        self.istio_init_containers = istio_init_containers
        self.istio_containers = istio_containers

    def __str__(self):
        return 'name:{}, created_at:{}, created_by:{},\
            istio_init_containers:{}, istio_containers:{}'.format(
            self.name, self.created_at, self.created_by,
            self.istio_init_containers, self.istio_containers)

    def __repr__(self):
        return "{}({}, {}, {}, {}, {}, {})".format(
            type(self).__name__, repr(self.name),
            repr(self.created_at), repr(self.created_by),
            repr(self.istio_init_containers), repr(self.istio_containers))

    def __eq__(self, other):
        return self.is_equal(other, advanced_check=True)

    def is_equal(self, other, advanced_check=True):
        # basic check
        if not isinstance(other, WorkloadPod):
            return False
        if self.name != other.name:
            return False
        # TODO compare multiple created at dates
        # if self.created_at != other.created_at:
        #    return False
        if self.created_by != other.created_by:
            return False
        # advanced check
        if advanced_check:
            if self.istio_init_containers != other.istio_init_containers:
                return False
            if self.istio_containers != other.istio_containers:
                return False
        return True
